/**
 * @module layout-toggle
 * @description Alpine.js component for toggling between normal and wide
 * page layouts. Persists the user's preference in ``localStorage``
 * (key ``lumina-layout``) and updates the ``data-layout`` attribute
 * on ``<html>``.
 */

/**
 * Factory for the layout-toggle Alpine component.
 * Registered as ``Alpine.data("layoutToggle", layoutToggle)``.
 *
 * **Properties:**
 *
 * - ``wide`` *(boolean)* — Whether wide layout is currently active.
 *
 * **Methods:**
 *
 * - ``init()`` — Reads stored preference and applies the layout.
 * - ``toggle()`` — Flips between normal and wide layout.
 * - ``apply()`` — Applies the current layout to ``document.documentElement``.
 *
 * @function layoutToggle
 * @returns {object} Alpine.js component data.
 */
export default function layoutToggle() {
  return {
    wide: false,

    init() {
      try {
        this.wide = localStorage.getItem("lumina-layout") === "wide";
      } catch {
        this.wide = false;
      }
      this.apply();
    },

    toggle() {
      this.wide = !this.wide;
      this.apply();
    },

    apply() {
      // Apply the visual change first — persistence is best-effort and
      // must not block the actual layout switch if storage throws.
      if (this.wide) {
        document.documentElement.setAttribute("data-layout", "wide");
      } else {
        document.documentElement.removeAttribute("data-layout");
      }
      try {
        if (this.wide) {
          localStorage.setItem("lumina-layout", "wide");
        } else {
          localStorage.removeItem("lumina-layout");
        }
      } catch {
        /* ignore — layout still applied for this page view */
      }
    },
  };
}
