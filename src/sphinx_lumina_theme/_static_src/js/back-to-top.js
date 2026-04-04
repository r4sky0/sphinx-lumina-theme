export default function backToTop() {
  return {
    visible: false,
    _lastScrollY: 0,
    _threshold: 300,

    init() {
      this._lastScrollY = window.scrollY;
      this._scrollHandler = () => this._onScroll();
      window.addEventListener("scroll", this._scrollHandler, {
        passive: true,
      });
    },

    destroy() {
      window.removeEventListener("scroll", this._scrollHandler);
    },

    _onScroll() {
      const y = window.scrollY;
      if (y < this._threshold) {
        this.visible = false;
      } else if (y < this._lastScrollY) {
        // Scrolling up
        this.visible = true;
      } else {
        // Scrolling down
        this.visible = false;
      }
      this._lastScrollY = y;
    },

    scrollToTop() {
      const prefersReduced = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
      ).matches;
      window.scrollTo({
        top: 0,
        behavior: prefersReduced ? "instant" : "smooth",
      });
    },
  };
}
