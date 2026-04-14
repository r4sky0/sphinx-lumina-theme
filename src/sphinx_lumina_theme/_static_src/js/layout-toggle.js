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
      this.wide = localStorage.getItem("lumina-layout") === "wide";
      this.apply();
    },

    toggle() {
      this.wide = !this.wide;
      this.apply();
    },

    apply() {
      if (this.wide) {
        document.documentElement.setAttribute("data-layout", "wide");
        localStorage.setItem("lumina-layout", "wide");
      } else {
        document.documentElement.removeAttribute("data-layout");
        localStorage.removeItem("lumina-layout");
      }
    },
  };
}
