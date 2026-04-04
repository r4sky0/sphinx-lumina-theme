import DOMPurify from "dompurify";

const EXCERPT_CONFIG = { ALLOWED_TAGS: ["mark"], ALLOWED_ATTR: [] };

export default function searchModal() {
  return {
    open: false,
    query: "",
    results: [],
    selectedIndex: 0,
    loaded: false,
    error: null,
    pagefind: null,
    _trigger: null,
    _trapHandler: null,
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
        el.textContent = isMac ? "\u2318K" : "Ctrl+K";
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
      if (this.backend === "pagefind") {
        try {
          const pagefindUrl = new URL(`${this.baseUrl}_pagefind/pagefind.js`, document.baseURI).href;
          this.pagefind = await import(pagefindUrl);
          await this.pagefind.init();
          this.loaded = true;
        } catch (e) {
          this.error =
            "Search requires Pagefind indexing. Use your browser\u2019s Ctrl+F to search this page, or run: pagefind --site _build/html/";
          this.loaded = true;
        }
      } else {
        this.loaded = true;
      }
    },

    async search() {
      if (!this.query || !this.loaded) return;
      this.selectedIndex = 0;

      if (this.backend === "pagefind" && this.pagefind) {
        const search = await this.pagefind.search(this.query);
        const results = await Promise.all(
          search.results.slice(0, 10).map((r) => r.data())
        );
        this.results = results.map((r) => ({
          title: r.meta?.title || "Untitled",
          url: r.url,
          excerpt: DOMPurify.sanitize(r.excerpt, EXCERPT_CONFIG),
        }));
      } else {
        this.results = [
          {
            title: 'Search for "' + this.query + '"',
            url: "search.html?q=" + encodeURIComponent(this.query),
            excerpt: "Open Sphinx search results page",
          },
        ];
      }
    },

    moveDown() {
      if (this.selectedIndex < this.results.length - 1) this.selectedIndex++;
    },

    moveUp() {
      if (this.selectedIndex > 0) this.selectedIndex--;
    },

    goToSelected() {
      if (this.results[this.selectedIndex]) {
        window.location.href = this.results[this.selectedIndex].url;
      }
    },
  };
}
