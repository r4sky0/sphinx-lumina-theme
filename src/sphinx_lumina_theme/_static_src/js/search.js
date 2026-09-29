/**
 * @module search
 * @description Alpine.js component for the full-text search modal. Supports
 * Pagefind as the primary backend with a fallback to Sphinx's built-in
 * search. Provides keyboard navigation (arrow keys, Enter, Escape),
 * a native dialog, and the ``/`` and ``Ctrl+K`` / ``⌘K`` shortcuts.
 */

import DOMPurify from "dompurify";

const EXCERPT_CONFIG = { ALLOWED_TAGS: ["mark"], ALLOWED_ATTR: [] };
/* If Pagefind hasn't initialized in this many ms, give up and fall back to
   the Sphinx search page so the modal doesn't sit on "Loading…" forever. */
const PAGEFIND_LOAD_TIMEOUT_MS = 5000;
/* Number of recent queries to memoize. Pagefind is fast but not free, and
   users routinely retype the same query when navigating around. */
const QUERY_CACHE_LIMIT = 10;

/**
 * Factory for the search modal Alpine component.
 * Registered as ``Alpine.data("searchModal", searchModal)``.
 *
 * **Properties:**
 *
 * - ``query`` *(string)* — Current search input value.
 * - ``results`` *(Array)* — Page and heading links in keyboard navigation order.
 * - ``scope`` *(string)* — Selected section; empty means all documentation.
 * - ``scopes`` *(Array)* — Section names available in the index.
 * - ``searching`` *(boolean)* — Whether the current query is pending.
 * - ``selectedIndex`` *(number)* — Index of the keyboard-highlighted result.
 * - ``loaded`` *(boolean)* — Whether the search engine has been initialized.
 * - ``error`` *(string|null)* — Error message, if search initialization failed.
 * - ``backend`` *(string)* — Search backend: ``"pagefind"`` or ``"sphinx"``.
 *
 * **Methods:**
 *
 * - ``init()`` — Sets up keyboard shortcuts and trigger buttons.
 * - ``toggle()`` — Opens or closes the modal.
 * - ``openModal()`` — Opens the modal, loads the search engine on first use.
 * - ``close()`` — Closes the modal and restores focus.
 * - ``search()`` — Runs a search query and populates results.
 * - ``moveDown()`` — Moves keyboard selection down.
 * - ``moveUp()`` — Moves keyboard selection up.
 * - ``goToSelected()`` — Navigates to the selected result.
 *
 * @function searchModal
 * @returns {object} Alpine.js component data.
 */
export default function searchModal() {
  return {
    query: "",
    results: [],
    scope: "",
    scopes: [],
    searching: false,
    _requestId: 0,
    selectedIndex: 0,
    loaded: false,
    error: null,
    pagefind: null,
    _trigger: null,
    _resultCache: new Map(),
    backend:
      document.querySelector('meta[name="lumina-search-backend"]')?.content ||
      "pagefind",
    baseUrl:
      document.querySelector('meta[name="lumina-base-url"]')?.content || "/",

    async init() {
      document.querySelectorAll("[data-search-trigger]").forEach((btn) => {
        btn.addEventListener("click", () => this.toggle(btn));
      });

      // "/" shortcut — open search when not typing in an input
      document.addEventListener("keydown", (e) => {
        if (e.key !== "/") return;
        if (this.$el.open) return;
        const tag = document.activeElement?.tagName;
        const editable = document.activeElement?.isContentEditable;
        if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || editable) return;
        e.preventDefault();
        this.openModal();
      });

      // Platform-aware kbd badge
      const platform = navigator.userAgentData?.platform ?? navigator.platform ?? "";
      const isMac = /mac|iphone|ipod|ipad/i.test(platform);
      document.querySelectorAll("[data-search-shortcut]").forEach((el) => {
        el.textContent = isMac ? "⌘K" : "Ctrl+K";
      });
    },

    toggle(trigger) {
      this.$el.open ? this.close() : this.openModal(trigger);
    },

    async openModal(trigger) {
      if (this.$el.open) return;
      this._trigger = trigger || document.activeElement;
      this.query = "";
      this.scope = "";
      this.searching = false;
      this._requestId++;
      this.results = [];
      this.selectedIndex = 0;
      this.error = null;

      this.$el.showModal();
      await this.$nextTick();
      this.$refs.searchInput?.focus();

      if (!this.loaded) {
        await this.loadSearchEngine();
      }
      if (this.$el.open) await this.search();
    },

    close() {
      this._requestId++;
      if (this.$el.open) this.$el.close();
      this._trigger?.focus();
      this._trigger = null;
    },

    async loadSearchEngine() {
      if (this.backend !== "pagefind") {
        this.loaded = true;
        return;
      }
      try {
        const pagefindUrl = new URL(
          `${this.baseUrl}_pagefind/pagefind.js`,
          document.baseURI,
        ).href;
        // Race the dynamic import against a timeout so a slow/missing index
        // doesn't leave the modal stuck on "Loading…".
        let timer;
        const timeout = new Promise((_, reject) => {
          timer = setTimeout(
            () => reject(new Error("Pagefind load timed out")),
            PAGEFIND_LOAD_TIMEOUT_MS,
          );
        });
        try {
          this.pagefind = await Promise.race([import(pagefindUrl), timeout]);
        } finally {
          clearTimeout(timer);
        }
        await this.pagefind.init();
        try {
          const filters = await this.pagefind.filters();
          this.scopes = Object.keys(filters.section || {});
        } catch {
          // An older index can still provide ordinary full-text search.
          this.scopes = [];
        }
        this.loaded = true;
      } catch (e) {
        this.pagefind = null;
        this.scopes = [];
        this.error = "Instant search is unavailable. Use Sphinx search below.";
        this.loaded = true;
      }
    },

    async search() {
      this.error = null;
      const requestId = ++this._requestId;
      const query = this.query.trim();
      const scope = this.scope;
      this.selectedIndex = 0;
      this.searching = false;
      this.results = [];
      if (!query || !this.loaded) return;

      const key = JSON.stringify([query, scope]);
      const cached = this._resultCache.get(key);
      if (cached) {
        this.error = null;
        this.results = cached;
        return;
      }

      this.searching = true;
      this.error = null;
      try {
        let results;
        if (this.backend === "pagefind" && this.pagefind) {
          const search = await this.pagefind.search(query, {
            filters: scope ? { section: scope } : {},
          });
          const data = await Promise.all(
            search.results.slice(0, 10).map((r) => r.data()),
          );
          results = data.flatMap((r) => {
            const page = {
              title: r.meta?.title || "Untitled",
              url: r.url,
              excerpt: DOMPurify.sanitize(r.excerpt, EXCERPT_CONFIG),
              breadcrumb: r.meta?.breadcrumb || "",
              isHeading: false,
            };
            const headings = (r.sub_results || [])
              .filter((sub) => sub.anchor && sub.anchor.element !== "h1")
              .slice(0, 3)
              .map((sub) => ({
                title: sub.title,
                url: sub.url,
                excerpt: DOMPurify.sanitize(sub.excerpt, EXCERPT_CONFIG),
                breadcrumb: "",
                isHeading: true,
              }));
            return [page, ...headings];
          });
          this._cacheResults(key, results);
        } else {
          results = this.fallbackResults(query);
        }
        if (requestId !== this._requestId || query !== this.query.trim() || scope !== this.scope) return;
        this.results = results;
      } catch {
        if (requestId !== this._requestId || query !== this.query.trim() || scope !== this.scope) return;
        this.error = "Instant search is unavailable. Sphinx search covers all docs.";
        this.results = this.fallbackResults(query);
      } finally {
        if (requestId === this._requestId) this.searching = false;
      }
    },

    fallbackResults(query) {
      return [{
        title: 'Search for "' + query + '"',
        url: this.baseUrl + "search.html?q=" + encodeURIComponent(query),
        excerpt: "Open Sphinx search results page",
        breadcrumb: "",
        isHeading: false,
      }];
    },

    searchAll() {
      this.scope = "";
      this.search();
      this.$refs.searchInput?.focus();
    },

    _cacheResults(query, results) {
      // Evict the oldest entry (Map keeps insertion order) before inserting
      // the new one so the cache stays bounded.
      if (this._resultCache.size >= QUERY_CACHE_LIMIT) {
        const oldest = this._resultCache.keys().next().value;
        this._resultCache.delete(oldest);
      }
      this._resultCache.set(query, results);
    },

    moveDown() {
      if (this.selectedIndex < this.results.length - 1) this.selectedIndex++;
      this.scrollToSelected();
    },

    moveUp() {
      if (this.selectedIndex > 0) this.selectedIndex--;
      this.scrollToSelected();
    },

    scrollToSelected() {
      this.$nextTick(() => {
        this.$el.querySelectorAll("[data-search-result]")[this.selectedIndex]
          ?.scrollIntoView({ block: "nearest" });
      });
    },

    goToSelected() {
      if (this.results[this.selectedIndex]) {
        window.location.href = this.results[this.selectedIndex].url;
      }
    },
  };
}
