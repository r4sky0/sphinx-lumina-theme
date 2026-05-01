/**
 * @module sidebar
 * @description Alpine.js component for the mobile sidebar drawer.
 * Manages open/close state, body scroll locking, ARIA attributes,
 * focus trapping, and focus return to the trigger on close.
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
    _trapHandler: null,

    toggle() {
      this.mobileOpen = !this.mobileOpen;
      document.body.style.overflow = this.mobileOpen ? "hidden" : "";
      this._updateAria();

      if (this.mobileOpen) {
        this._trigger = document.activeElement;
        this._trapHandler = (e) => this._handleFocusTrap(e);
        document.addEventListener("keydown", this._trapHandler);
        this.$nextTick(() => {
          document.querySelector("[data-sidebar-close]")?.focus();
        });
      } else {
        this._teardownFocusTrap();
      }
    },

    close() {
      this.mobileOpen = false;
      document.body.style.overflow = "";
      this._updateAria();
      this._teardownFocusTrap();
      this._trigger?.focus();
      this._trigger = null;
    },

    _teardownFocusTrap() {
      if (this._trapHandler) {
        document.removeEventListener("keydown", this._trapHandler);
        this._trapHandler = null;
      }
    },

    /* Keep Tab cycling within the drawer while it's open so keyboard users
       can't reach the (visually hidden) page content behind it. */
    _handleFocusTrap(e) {
      if (e.key !== "Tab" || !this.mobileOpen) return;
      const drawer = document.getElementById("lumina-sidebar-drawer");
      if (!drawer) return;

      const focusable = drawer.querySelectorAll(
        'a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])',
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
