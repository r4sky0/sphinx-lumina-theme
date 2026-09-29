/**
 * @module announcement
 * @description Alpine.js component for a dismissible announcement banner.
 * Reads a ``data-announcement-id`` attribute from the host element and
 * persists dismissal state in ``localStorage`` so the banner stays
 * hidden on subsequent page loads.
 */

/**
 * Factory for the announcement banner Alpine component.
 * Registered as ``Alpine.data("announcementBanner", announcementBanner)``.
 *
 * **Methods:**
 *
 * - ``init()`` — Reads the announcement ID and tracks the banner height.
 * - ``destroy()`` — Disconnects the resize observer.
 * - ``dismiss()`` — Hides the banner and persists the dismissal in localStorage.
 *
 * @function announcementBanner
 * @returns {object} Alpine.js component data.
 */
export default function announcementBanner() {
  let _id = null;
  let _resizeObserver = null;
  return {
    init() {
      _id = this.$el.getAttribute("data-announcement-id");
      _resizeObserver = new ResizeObserver(() => {
        document.documentElement.style.setProperty(
          "--lumina-announcement-height", `${this.$el.getBoundingClientRect().height}px`,
        );
      });
      _resizeObserver.observe(this.$el);
    },

    destroy() {
      _resizeObserver.disconnect();
      document.documentElement.style.removeProperty("--lumina-announcement-height");
    },

    dismiss() {
      if (_id) {
        localStorage.setItem("lumina-announce-" + _id, "1");
      }
      document.documentElement.classList.remove("has-announcement");
    },
  };
}
