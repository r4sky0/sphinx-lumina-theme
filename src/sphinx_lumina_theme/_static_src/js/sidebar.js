/**
 * @module sidebar
 * @description Alpine.js component for the mobile sidebar drawer.
 * Manages open/close state, body scroll locking, ARIA attributes,
 * and focus management (returns focus to the trigger on close).
 * Auto-closes when the viewport crosses the ``1024px`` breakpoint.
 */

/**
 * Factory for the sidebar Alpine component.
 * Registered as ``Alpine.data("sidebar", sidebar)``.
 *
 * **Properties:**
 *
 * - ``mobileOpen`` *(boolean)* — Whether the mobile sidebar is visible.
 *
 * **Methods:**
 *
 * - ``toggle()`` — Toggles the sidebar and locks/unlocks body scroll.
 * - ``close()`` — Closes the sidebar and restores focus.
 * - ``init()`` — Attaches toggle button handlers and a media-query listener.
 *
 * @function sidebar
 * @returns {object} Alpine.js component data.
 */
export default function sidebar() {
  return {
    mobileOpen: false,
    _trigger: null,

    toggle() {
      this.mobileOpen = !this.mobileOpen;
      document.body.style.overflow = this.mobileOpen ? "hidden" : "";
      this._updateAria();

      if (this.mobileOpen) {
        this._trigger = document.activeElement;
        this.$nextTick(() => {
          document.querySelector("[data-sidebar-close]")?.focus();
        });
      }
    },

    close() {
      this.mobileOpen = false;
      document.body.style.overflow = "";
      this._updateAria();
      this._trigger?.focus();
      this._trigger = null;
    },

    _updateAria() {
      document.querySelectorAll("[data-sidebar-toggle]").forEach((btn) => {
        btn.setAttribute("aria-expanded", String(this.mobileOpen));
      });
    },

    init() {
      document.querySelectorAll("[data-sidebar-toggle]").forEach((btn) => {
        btn.addEventListener("click", () => this.toggle());
      });

      const mql = window.matchMedia("(min-width: 1024px)");
      mql.addEventListener("change", (e) => {
        if (e.matches) this.close();
      });
    },
  };
}
