/**
 * @module scrollspy
 * @description Alpine.js component that highlights the active table-of-contents
 * link as the user scrolls. Uses ``IntersectionObserver`` to track the current
 * heading and a clip-path sliding indicator for smooth visual feedback.
 */

/**
 * Factory for the scrollspy Alpine component.
 * Registered as ``Alpine.data("scrollspy", scrollspy)``.
 *
 * **Properties:**
 *
 * - ``activeId`` *(string|null)* — The ``id`` of the currently visible section.
 *
 * **Methods:**
 *
 * - ``init()`` — Creates the indicator, computes positions, starts observers.
 * - ``destroy()`` — Disconnects observers and removes the indicator element.
 *
 * @function scrollspy
 * @returns {object} Alpine.js component data.
 */
export default function scrollspy() {
  return {
    activeId: null,
    _observer: null,
    _resizeObserver: null,
    _indicator: null,
    _links: [],
    _positions: new Map(),
    _rafId: null,

    init() {
      const nav = this.$el;
      // Cache the id ↔ link mapping once. The TOC markup is static for the
      // page's lifetime, so re-querying on every scroll/resize is wasted work.
      this._links = Array.from(nav.querySelectorAll("a"))
        .map((a) => {
          const href = a.getAttribute("href");
          return href && href.startsWith("#") ? { id: href.slice(1), el: a } : null;
        })
        .filter(Boolean);

      if (this._links.length === 0) return;

      this._indicator = document.createElement("div");
      this._indicator.className = "lumina-toc-indicator";
      this._indicator.setAttribute("aria-hidden", "true");
      nav.appendChild(this._indicator);

      this._computePositions();
      // Coalesce ResizeObserver bursts (multiple ticks per frame during a
      // window drag) into a single recompute via requestAnimationFrame.
      this._resizeObserver = new ResizeObserver(() => this._scheduleRecompute());
      this._resizeObserver.observe(nav);

      this._observer = new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (entry.isIntersecting) {
              this.activeId = entry.target.id;
              this._updateActive();
              this._updateIndicator();
              break;
            }
          }
        },
        { rootMargin: "-80px 0px -60% 0px" },
      );

      for (const { id } of this._links) {
        const el = document.getElementById(id);
        if (el) this._observer.observe(el);
      }
    },

    _scheduleRecompute() {
      if (this._rafId !== null) return;
      this._rafId = requestAnimationFrame(() => {
        this._rafId = null;
        this._computePositions();
        if (this.activeId) this._updateIndicator();
      });
    },

    _computePositions() {
      this._positions.clear();
      for (const { id, el } of this._links) {
        this._positions.set(id, [el.offsetTop, el.offsetTop + el.offsetHeight]);
      }
    },

    _updateActive() {
      for (const { id, el } of this._links) {
        el.classList.toggle("lumina-toc-active", id === this.activeId);
      }
    },

    _updateIndicator() {
      if (!this._indicator || !this.activeId) return;
      const pos = this._positions.get(this.activeId);
      if (!pos) return;
      const [top, bottom] = pos;
      this._indicator.style.setProperty("--ind-top", `${top}px`);
      this._indicator.style.setProperty("--ind-bottom", `${bottom}px`);
    },

    destroy() {
      if (this._observer) this._observer.disconnect();
      if (this._resizeObserver) this._resizeObserver.disconnect();
      if (this._rafId !== null) cancelAnimationFrame(this._rafId);
      if (this._indicator) this._indicator.remove();
    },
  };
}
