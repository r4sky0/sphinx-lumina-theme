/**
 * @module version-switcher
 * @description Alpine.js component for switching between documentation
 * versions. Fetches a JSON manifest of available versions and lets the
 * user navigate to the same page on a different version's URL.
 */

/**
 * Factory for the version-switcher Alpine component.
 * Registered as ``Alpine.data("versionSwitcher", versionSwitcher)``.
 *
 * **Properties:**
 *
 * - ``open`` *(boolean)* — Whether the version dropdown is visible.
 * - ``versions`` *(Array)* — Fetched array of ``{ version, name, url }`` objects.
 * - ``currentLabel`` *(string)* — Display label for the active version.
 * - ``error`` *(boolean)* — Whether version fetching failed.
 *
 * **Methods:**
 *
 * - ``init()`` — Reads config attributes and fetches the version manifest.
 * - ``toggle()`` — Toggles the dropdown open/closed.
 *
 * @function versionSwitcher
 * @returns {object} Alpine.js component data.
 */
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
      // to the same page on a different version's URL. The meta tag holds
      // a page-relative path to the docs root (e.g. "../"), so it must be
      // resolved against the current URL before comparing pathnames.
      const baseUrl = document.querySelector('meta[name="lumina-base-url"]');
      if (baseUrl) {
        try {
          const root = new URL(
            baseUrl.getAttribute("content") || ".",
            window.location.href,
          );
          const current = window.location.pathname;
          this.relPath = current.startsWith(root.pathname)
            ? current.slice(root.pathname.length)
            : current.replace(/^\//, "");
        } catch {
          this.relPath = "";
        }
      }

      if (jsonUrl) {
        this._fetchVersions(jsonUrl);
      }
    },

    toggle() {
      this.open = !this.open;
    },

    _versionUrl(v) {
      // Safely join version base URL with current page's relative path.
      // The trailing slash matters: without it the last path segment of
      // ``v.url`` would be replaced instead of appended to.
      try {
        const base = v.url.endsWith("/") ? v.url : v.url + "/";
        return new URL(this.relPath, base).href;
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
