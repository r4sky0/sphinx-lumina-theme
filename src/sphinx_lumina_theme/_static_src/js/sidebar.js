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
        setTimeout(() => {
          document.querySelector("[data-sidebar-close]")?.focus();
        }, 260);
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
