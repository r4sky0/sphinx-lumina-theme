/**
 * @module shortcuts-modal
 * @description Alpine.js component for the keyboard-shortcuts overlay.
 * Triggered by ``?`` (when not typing in an input) or by any element with
 * ``data-shortcuts-trigger``. Dismissed with ``Esc`` or by clicking the
 * backdrop. Maintains a focus trap and returns focus to the triggering
 * element on close.
 */

export default function shortcutsModal() {
  return {
    open: false,
    _trigger: null,
    _trapHandler: null,
    _isMac: false,

    init() {
      const platform = navigator.userAgentData?.platform ?? navigator.platform ?? "";
      this._isMac = /mac|iphone|ipod|ipad/i.test(platform);

      document.querySelectorAll("[data-shortcuts-trigger]").forEach((btn) => {
        btn.addEventListener("click", () => this.toggle());
      });

      document.addEventListener("keydown", (e) => {
        if (e.key !== "?") return;
        if (this.open) return;
        const tag = document.activeElement?.tagName;
        const editable = document.activeElement?.isContentEditable;
        if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || editable) return;
        e.preventDefault();
        this.openModal();
      });
    },

    get modKey() {
      return this._isMac ? "\u2318" : "Ctrl";
    },

    toggle() {
      this.open ? this.close() : this.openModal();
    },

    async openModal() {
      this._trigger = document.activeElement;
      this.open = true;
      await this.$nextTick();
      this.$refs.dialog?.focus();

      this._trapHandler = (e) => this._handleFocusTrap(e);
      document.addEventListener("keydown", this._trapHandler);
    },

    close() {
      this.open = false;
      if (this._trapHandler) {
        document.removeEventListener("keydown", this._trapHandler);
        this._trapHandler = null;
      }
      this._trigger?.focus();
      this._trigger = null;
    },

    _handleFocusTrap(e) {
      if (e.key !== "Tab" || !this.open) return;
      const modal = document.getElementById("lumina-shortcuts-modal");
      if (!modal) return;
      const focusable = modal.querySelectorAll(
        'button, a[href], [tabindex]:not([tabindex="-1"])'
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
  };
}
