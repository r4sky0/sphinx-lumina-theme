/**
 * @module icon-browser
 * @description Alpine.js component for the icon browser page.
 * Provides search filtering and click-to-copy for icon names.
 */
import { copyText } from "./utils/clipboard.js";

export default function iconBrowser() {
  return {
    query: "",
    toast: false,
    copiedName: "",
    visible: 0,
    _toastTimeout: null,

    init() {
      this.visible = document.querySelectorAll(".lumina-icon-cell").length;
    },

    filter() {
      const q = this.query.toLowerCase().trim();
      let count = 0;
      document.querySelectorAll(".lumina-icon-cell").forEach((el) => {
        const name = el.dataset.iconName;
        const show = !q || name.includes(q);
        el.style.display = show ? "" : "none";
        if (show) count++;
      });
      this.visible = count;
    },

    matches(name) {
      if (!this.query) return true;
      return name.includes(this.query.toLowerCase().trim());
    },

    async copy(name) {
      try {
        await copyText(name);
      } catch (err) {
        console.warn("Lumina: copy failed —", err.message);
        return;
      }
      this.copiedName = name;
      this.toast = true;
      clearTimeout(this._toastTimeout);
      this._toastTimeout = setTimeout(() => {
        this.toast = false;
      }, 1500);
    },
  };
}
