/**
 * @module header-offset
 * @description Keeps the shared layout offset synchronized with the rendered
 * fixed header, including wrapped announcements and dismissed banners.
 */

/**
 * Factory for the header offset Alpine component.
 * Registered as ``Alpine.data("headerOffset", headerOffset)``.
 *
 * @function headerOffset
 * @returns {object} Alpine.js component data.
 */
export default function headerOffset() {
  return {
    init() {
      const update = () => {
        const height = this.$el.getBoundingClientRect().height;
        if (height > 0) {
          document.documentElement.style.setProperty(
            "--lumina-header-offset",
            `${Math.ceil(height)}px`,
          );
        }
      };

      update();
      if (typeof ResizeObserver !== "undefined") {
        this._resizeObserver = new ResizeObserver(update);
        this._resizeObserver.observe(this.$el);
      } else {
        window.addEventListener("resize", update);
      }
    },
  };
}
