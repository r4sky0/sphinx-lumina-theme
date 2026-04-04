export default function versionSwitcher() {
  return {
    open: false,
    versions: [],
    match: "",
    currentLabel: "",
    relPath: "",
    error: false,

    init() {
      const el = this.$el;
      const jsonUrl = el.getAttribute("data-json-url");
      this.match = el.getAttribute("data-version-match") || "";

      // Compute the relative path within the docs so we can navigate
      // to the same page on a different version's URL
      const baseUrl = document.querySelector('meta[name="lumina-base-url"]');
      if (baseUrl) {
        const base = baseUrl.getAttribute("content").replace(/\/$/, "");
        const current = window.location.pathname;
        this.relPath = current.startsWith(base)
          ? current.slice(base.length)
          : current;
      }

      if (jsonUrl) {
        this._fetchVersions(jsonUrl);
      }
    },

    toggle() {
      this.open = !this.open;
    },

    async _fetchVersions(url) {
      try {
        const resp = await fetch(url);
        if (!resp.ok) {
          this.error = true;
          return;
        }
        const data = await resp.json();
        this.versions = data;

        // Find the current version and set the display label
        const current = data.find((v) => v.version === this.match);
        if (current) {
          this.currentLabel = current.name || current.version;
        }
      } catch {
        this.error = true;
      }
    },
  };
}
