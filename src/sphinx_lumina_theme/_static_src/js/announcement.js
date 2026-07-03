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
 * - ``init()`` — Reads the announcement ID from ``data-announcement-id``.
 * - ``dismiss()`` — Hides the banner and persists the dismissal in localStorage.
 *
 * @function announcementBanner
 * @returns {object} Alpine.js component data.
 */
export default function announcementBanner() {
  let _id = null;
  return {
    init() {
      _id = this.$el.getAttribute("data-announcement-id");
    },

    dismiss() {
      // Hide the banner first — persistence is best-effort and must not
      // block the dismiss action if storage throws (private browsing,
      // disabled site data, quota exceeded).
      document.documentElement.classList.remove("has-announcement");
      if (_id) {
        try {
          localStorage.setItem("lumina-announce-" + _id, "1");
        } catch {
          /* ignore — banner stays dismissed for this page view */
        }
      }
    },
  };
}
