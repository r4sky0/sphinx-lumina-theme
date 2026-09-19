/**
 * @module search
 * @description Alpine.js component for the full-text search modal. Supports
 * Pagefind as the primary backend with a fallback to Sphinx's built-in
 * search. Provides keyboard navigation (arrow keys, Enter, Escape),
 * a focus trap, and the ``/`` and ``Ctrl+K`` / ``⌘K`` shortcuts.
 */

import DOMPurify from "dompurify";

const EXCERPT_CONFIG = { ALLOWED_TAGS: ["mark"], ALLOWED_ATTR: [] };
/* If Pagefind hasn't initialized in this many ms, give up and fall back to
   the Sphinx search page so the modal doesn't sit on "Loading…" forever. */
const PAGEFIND_LOAD_TIMEOUT_MS = 5000;
/* Number of recent queries to memoize. Pagefind is fast but not free, and
   users routinely retype the same query when navigating around. */
const QUERY_CACHE_LIMIT = 10;

const DEFAULT_MESSAGES = {
  dialogLabel: "Search documentation",
  loading: "Loading search index...",
  noResults: "No results found.",
  typeToSearch: "Type to search...",
  navigate: "Navigate",
  open: "Open",
  close: "Close",
  unavailable: "Pagefind is unavailable. Using built-in search.",
  queryFailed: "Search failed. Using built-in search.",
  searchFor: "Search for",
  fallbackExcerpt: "Open built-in search results",
  result: "result",
  results: "results",
};

function getMessages() {
  const element = document.getElementById("lumina-i18n");
  if (!element) return DEFAULT_MESSAGES;
  try {
    return { ...DEFAULT_MESSAGES, ...JSON.parse(element.textContent) };
  } catch {
    return DEFAULT_MESSAGES;
  }
}

function sectionFromUrl(url) {
  const segments = url.split("?")[0].split("#")[0]
    .replace(/\.html$/, "")
    .split("/")
    .filter(Boolean);
  if (segments.length < 2) return null;
  const slug = segments[segments.length - 2];
  return slug.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Factory for the search modal Alpine component.
 * Registered as ``Alpine.data("searchModal", searchModal)``.
 *
 * **Properties:**
 *
 * - ``open`` *(boolean)* — Whether the modal is visible.
 * - ``query`` *(string)* — Current search input value.
 * - ``results`` *(Array)* — Array of search result objects.
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
    open: false,
    query: "",
    results: [],
    selectedIndex: 0,
    loaded: false,
    error: null,
    pagefind: null,
    _loadPromise: null,
    _searchRequest: 0,
    messages: getMessages(),
    _trigger: null,
    _trapHandler: null,
    _resultCache: new Map(),
    backend:
      document.querySelector('meta[name="lumina-search-backend"]')?.content ||
      "pagefind",
    baseUrl:
      document.querySelector('meta[name="lumina-base-url"]')?.content || "/",

    async init() {
      document.querySelectorAll("[data-search-trigger]").forEach((btn) => {
        btn.addEventListener("click", () => this.toggle());
      });

      // "/" shortcut — open search when not typing in an input
      document.addEventListener("keydown", (e) => {
        if (e.key !== "/") return;
        if (this.open) return;
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

    toggle() {
      this.open ? this.close() : this.openModal();
    },

    async openModal() {
      this._trigger = document.activeElement;
      this.open = true;
      this.query = "";
      this.results = [];
      this.selectedIndex = 0;
      this.error = null;

      await this.$nextTick();
      this.$refs.searchInput?.focus();

      // Set up focus trap
      this._trapHandler = (e) => this._handleFocusTrap(e);
      document.addEventListener("keydown", this._trapHandler);

      if (!this.loaded) {
        await this.loadSearchEngine();
      }
    },

    close() {
      this.open = false;

      // Remove focus trap
      if (this._trapHandler) {
        document.removeEventListener("keydown", this._trapHandler);
        this._trapHandler = null;
      }

      // Return focus to trigger
      this._trigger?.focus();
      this._trigger = null;
    },

    _handleFocusTrap(e) {
      if (e.key !== "Tab" || !this.open) return;
      const modal = document.getElementById("lumina-search-modal");
      if (!modal) return;

      const focusable = modal.querySelectorAll(
        'input, button, a[href], [tabindex]:not([tabindex="-1"])'
      );
      if (focusable.length === 0) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    },

    async loadSearchEngine() {
      if (this.loaded) return;
      if (this._loadPromise) return this._loadPromise;

      this._loadPromise = (async () => {
        if (this.backend !== "pagefind") {
          this.loaded = true;
          return;
        }

        try {
          const pagefindUrl = new URL(
            `${this.baseUrl}_pagefind/pagefind.js`,
            document.baseURI,
          ).href;
          // Race import and init together so a slow or broken index cannot
          // leave the modal stuck on "Loading…".
          let timer;
          const timeout = new Promise((_, reject) => {
            timer = setTimeout(
              () => reject(new Error("Pagefind initialization timed out")),
              PAGEFIND_LOAD_TIMEOUT_MS,
            );
          });
          try {
            this.pagefind = await Promise.race([
              import(pagefindUrl).then(async (module) => {
                const engine = module.default || module;
                await engine.init();
                return engine;
              }),
              timeout,
            ]);
          } finally {
            clearTimeout(timer);
          }
        } catch {
          // A failed engine must not be retained: subsequent searches use the
          // built-in Sphinx endpoint immediately and can recover on retry.
          this.pagefind = null;
          this.backend = "sphinx";
          this.error = this.messages.unavailable;
        } finally {
          this.loaded = true;
        }
      })();

      try {
        await this._loadPromise;
      } finally {
        this._loadPromise = null;
      }
    },

    async search() {
      const request = ++this._searchRequest;
      const query = this.query;
      if (!this.query) {
        // Clearing the input must also clear the previous query's results.
        this.results = [];
        this.selectedIndex = 0;
        return;
      }

      if (!this.loaded) await this.loadSearchEngine();
      if (request !== this._searchRequest || query !== this.query) return;
      this.selectedIndex = 0;

      const cached = this._resultCache.get(query);
      if (cached) {
        this.results = cached;
        return;
      }

      // Snapshot the query so a slow response can't clobber the results of
      // a newer search that resolved first.
      let results;
      try {
        if (this.backend === "pagefind" && this.pagefind) {
          const search = await this.pagefind.search(query);
          const data = await Promise.all(
            search.results.slice(0, 10).map((r) => r.data()),
          );
          results = data.map((r) => ({
            title: r.meta?.title || "Untitled",
            url: r.url,
            excerpt: DOMPurify.sanitize(r.excerpt, EXCERPT_CONFIG),
            section: sectionFromUrl(r.url),
          }));
        } else {
          results = this._fallbackResults(query);
        }
      } catch {
        this.pagefind = null;
        this.backend = "sphinx";
        this.error = this.messages.queryFailed;
        results = this._fallbackResults(query);
      }

      if (request !== this._searchRequest || query !== this.query) return;
      this._cacheResults(query, results);
      this.results = results;
    },

    _fallbackResults(query) {
      return [
        {
          title: `${this.messages.searchFor} "${query}"`,
          url: this.baseUrl + "search.html?q=" + encodeURIComponent(query),
          excerpt: this.messages.fallbackExcerpt,
        },
      ];
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
      this.$nextTick(() => this.scrollSelectedIntoView());
    },

    moveUp() {
      if (this.selectedIndex > 0) this.selectedIndex--;
      this.$nextTick(() => this.scrollSelectedIntoView());
    },

    scrollSelectedIntoView() {
      const selected = document.getElementById(
        `lumina-search-result-${this.selectedIndex}`,
      );
      selected?.scrollIntoView({ block: "nearest" });
    },

    goToSelected() {
      if (this.results[this.selectedIndex]) {
        window.location.href = this.results[this.selectedIndex].url;
      }
    },
  };
}
