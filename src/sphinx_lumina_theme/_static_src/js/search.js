/**
 * @module search
 * @description Alpine.js component for the full-text search modal. Supports
 * Pagefind as the primary backend with a fallback to Sphinx's built-in
 * search. Provides keyboard navigation (arrow keys, Enter, Escape),
 * a native dialog, and the ``/`` and ``Ctrl+K`` / ``⌘K`` shortcuts. API objects
 * from ``_static/lumina-symbols.json`` (written at build time from the Sphinx
 * domains) are matched by name and listed before the full-text results.
 */

import DOMPurify from "dompurify";

const EXCERPT_CONFIG = { ALLOWED_TAGS: ["mark"], ALLOWED_ATTR: [] };
/* If Pagefind hasn't initialized in this many ms, give up and fall back to
   the Sphinx search page so the modal doesn't sit on "Loading…" forever. */
const PAGEFIND_LOAD_TIMEOUT_MS = 5000;
/* Number of recent queries to memoize. Pagefind is fast but not free, and
   users routinely retype the same query when navigating around. */
const QUERY_CACHE_LIMIT = 10;
/* Symbol matches shown above the full-text results. */
const SYMBOL_LIMIT = 5;

/**
 * Rank API symbols by name: exact names and qualified suffixes first, then
 * name prefixes, then any part of the qualified name; shorter names win ties.
 *
 * @param {Array} symbols — Entries prepared by ``_loadSymbols()``.
 * @param {string} query — The trimmed search text.
 * @param {string} scope — Selected section; empty means all documentation.
 * @returns {Array} Result entries for the modal.
 */
function matchSymbols(symbols, query, scope) {
  const q = query.toLowerCase().replaceAll("#", ".");
  const ranked = [];
  for (const symbol of symbols) {
    if (scope && symbol.section !== scope) continue;
    let rank;
    if (symbol.base === q || symbol.qualified === q || symbol.qualified.endsWith("." + q)) rank = 0;
    else if (symbol.lower.startsWith(q)) rank = 1;
    else if (symbol.full.includes(q)) rank = 2;
    else continue;
    ranked.push([rank, symbol.lower.length, symbol]);
  }
  ranked.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  return ranked.slice(0, SYMBOL_LIMIT).map(([, , symbol]) => ({
    title: symbol.name,
    url: symbol.url,
    excerpt: "",
    breadcrumb: symbol.prefix ? `${symbol.kind} in ${symbol.prefix}` : symbol.kind,
    isHeading: false,
    isSymbol: true,
  }));
}

/**
 * Factory for the search modal Alpine component.
 * Registered as ``Alpine.data("searchModal", searchModal)``.
 *
 * **Properties:**
 *
 * - ``query`` *(string)* — Current search input value.
 * - ``results`` *(Array)* — Symbol, page and heading links in keyboard navigation order.
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
  // Thousands of entries on API sites; kept outside Alpine's reactive state.
  let symbols = [];
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
    _shownKey: null,
    backend:
      document.querySelector('meta[name="lumina-search-backend"]')?.content ||
      "pagefind",
    baseUrl:
      document.querySelector('meta[name="lumina-base-url"]')?.content || "/",

    async init() {
      document.querySelectorAll("[data-search-trigger]").forEach((btn) => {
        btn.addEventListener("click", () => this.toggle(btn));
      });

      // A result on the current page only changes the hash; close so the target shows.
      window.addEventListener("hashchange", () => {
        if (this.$el.open) this.close();
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
      this._shownKey = null;
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
      await Promise.all([this._loadPagefind(), this._loadSymbols()]);
      this.loaded = true;
    },

    async _loadSymbols() {
      try {
        const url = new URL(`${this.baseUrl}_static/lumina-symbols.json`, document.baseURI);
        const response = await fetch(url, { signal: AbortSignal.timeout(PAGEFIND_LOAD_TIMEOUT_MS) });
        if (!response.ok) return;
        const data = await response.json();
        symbols = data.symbols.map(([name, prefix, kind, page, anchor]) => {
          const [uri, section] = data.pages[page];
          const lower = name.toLowerCase();
          const base = lower.split("(", 1)[0];
          const owner = prefix ? prefix.toLowerCase() + "." : "";
          return {
            name,
            prefix,
            kind: data.kinds[kind],
            section,
            url: this.baseUrl + uri + (anchor ? "#" + anchor : ""),
            lower,
            base,
            qualified: owner + base,
            full: owner + lower,
          };
        });
      } catch {
        // Full-text search still works without symbols.
        symbols = [];
      }
    },

    async _loadPagefind() {
      if (this.backend !== "pagefind") return;
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
      } catch (e) {
        this.pagefind = null;
        this.scopes = [];
        this.error = "Instant search is unavailable. Use Sphinx search below.";
      }
    },

    async search() {
      const query = this.query.trim();
      const scope = this.scope;
      const key = JSON.stringify([query, scope]);
      // Opening the modal and the debounced input can both search for the same
      // text. Re-running it must not reset a selection the reader already moved.
      if (key === this._shownKey && this.results.length) return;
      this.error = null;
      const requestId = ++this._requestId;
      this._shownKey = null;
      this.selectedIndex = 0;
      this.searching = false;
      this.results = [];
      if (!query || !this.loaded) return;

      const cached = this._resultCache.get(key);
      if (cached) {
        this.error = null;
        this.results = cached;
        this._shownKey = key;
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
          results = [...matchSymbols(symbols, query, scope), ...results];
          this._cacheResults(key, results);
        } else {
          results = [...matchSymbols(symbols, query, scope), ...this.fallbackResults(query)];
        }
        if (requestId !== this._requestId || query !== this.query.trim() || scope !== this.scope) return;
        this.results = results;
        this._shownKey = key;
      } catch {
        if (requestId !== this._requestId || query !== this.query.trim() || scope !== this.scope) return;
        this.error = "Instant search is unavailable. Sphinx search covers all docs.";
        this.results = [...matchSymbols(symbols, query, scope), ...this.fallbackResults(query)];
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
