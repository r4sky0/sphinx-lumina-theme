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

    _versionUrl(v) {
      // Safely join version base URL with current page's relative path
      try {
        return new URL(this.relPath, v.url).href;
      } catch {
        return v.url;
      }
    },

    async _fetchVersions(url) {
      try {
        const resp = await fetch(url);
        if (!resp.ok) {
          this.error = true;
          return;
        }
        const data = await resp.json();
        if (!Array.isArray(data)) {
          this.error = true;
          return;
        }
        this.versions = data.filter(
          (v) => v && typeof v.version === "string" && typeof v.url === "string"
        );

        // Find the current version and set the display label
        const current = this.versions.find((v) => v.version === this.match);
        if (current) {
          this.currentLabel = current.name || current.version;
        }
      } catch {
        this.error = true;
      }
    },
  };
}
