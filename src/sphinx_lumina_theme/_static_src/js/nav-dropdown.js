export default function navDropdown() {
  return {
    open: false,
    _closeTimer: null,

    toggle() {
      this.open = !this.open;
    },

    show() {
      clearTimeout(this._closeTimer);
      this.open = true;
    },

    hide() {
      this._closeTimer = setTimeout(() => {
        this.open = false;
      }, 150);
    },

    cancelHide() {
      clearTimeout(this._closeTimer);
    },

    handleKeydown(e) {
      if (e.key === "Escape") {
        this.open = false;
        this.$refs.trigger?.focus();
      }
    },
  };
}
