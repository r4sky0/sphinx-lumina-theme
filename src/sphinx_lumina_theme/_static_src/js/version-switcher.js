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
    anchor: "",
    notice: "",
    messages: {},
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
      this.messages = this._getMessages();
      this.anchor = window.location.hash;
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

    _getMessages() {
      const element = document.getElementById("lumina-i18n");
      try {
        return {
          pageUnavailable:
            "This page is not available in this version. Opening its documentation home.",
          preview: "Preview",
          unsupported: "Unsupported",
          ...(element ? JSON.parse(element.textContent) : {}),
        };
      } catch {
        return {
          pageUnavailable:
            "This page is not available in this version. Opening its documentation home.",
          preview: "Preview",
          unsupported: "Unsupported",
        };
      }
    },

    _versionUrl(v) {
      // Safely join version base URL with current page's relative path.
      // The trailing slash matters: without it the last path segment of
      // ``v.url`` would be replaced instead of appended to.
      try {
        const base = v.url.endsWith("/") ? v.url : v.url + "/";
        const pageMap = v.pages || v.page_map || {};
        const mapped = Object.prototype.hasOwnProperty.call(pageMap, this.relPath)
          ? pageMap[this.relPath]
          : undefined;
        const unavailable =
          v.status === "unsupported" || v.supported === false || mapped === false;
        const destination =
          unavailable || mapped === undefined
            ? unavailable
              ? ""
              : this.relPath
            : typeof mapped === "string"
              ? mapped.replace(/^\//, "")
              : mapped && typeof mapped.path === "string"
                ? mapped.path.replace(/^\//, "")
                : "";
        const target = new URL(destination, base);
        if (destination && this.anchor) target.hash = this.anchor;
        v._pageAvailable = !unavailable && Boolean(destination);
        v._notice = v._pageAvailable ? "" : this.messages.pageUnavailable;
        return target.href;
      } catch {
        return v.url;
      }
    },

    targetUrl(v) {
      return v._targetUrl || this._versionUrl(v);
    },

    async _fetchVersions(url) {
      try {
        const resp = await fetch(url);
        if (!resp.ok) {
          this.error = true;
          return;
        }
        const data = await resp.json();
        const versions = Array.isArray(data) ? data : data?.versions;
        if (!Array.isArray(versions)) {
          this.error = true;
          return;
        }
        this.versions = versions.filter(
          (v) => v && typeof v.version === "string" && typeof v.url === "string"
        );
        this.versions.forEach((v) => {
          v._targetUrl = this._versionUrl(v);
          if (v.status === "preview") v._statusLabel = this.messages.preview;
          if (v.status === "unsupported") v._statusLabel = this.messages.unsupported;
        });

        // Find the current version and set the display label
        const current = this.versions.find((v) => v.version === this.match);
        if (current) {
          this.currentLabel = current.name || current.version;
          this.notice = current._notice || "";
        }
      } catch {
        this.error = true;
      }
    },
  };
}
