/**
 * @module scrollspy
 * @description Alpine.js component that highlights the active table-of-contents
 * link as the user scrolls. Tracks section starts at the reading line below
 * the fixed header, with a curved guide that follows the heading hierarchy.
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
    _resizeObserver: null,
    _scrollHandler: null,
    _indicator: null,
    _links: [],
    _positions: new Map(),
    _rafId: null,
    _needsMeasure: false,

    init() {
      const nav = this.$el;
      // Cache the id ↔ link mapping once. The TOC markup is static for the
      // page's lifetime, so re-querying on every scroll/resize is wasted work.
      this._links = Array.from(nav.querySelectorAll("a"))
        .map((a) => {
          const href = a.getAttribute("href");
          if (!href?.startsWith("#") || getComputedStyle(a).display === "none") return null;
          const id = href.slice(1);
          const target = document.getElementById(id);
          return target ? { id, el: a, target } : null;
        })
        .filter(Boolean);

      if (this._links.length === 0) return;

      this._indicator = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      this._indicator.classList.add("lumina-toc-guide");
      this._indicator.setAttribute("aria-hidden", "true");
      this._indicator.innerHTML = '<path class="lumina-toc-track" />'
        + '<path class="lumina-toc-indicator" /><circle r="2.5" />';
      nav.appendChild(this._indicator);

      this._computePositions();
      this._updateCurrent();
      this._scrollHandler = () => this._scheduleUpdate();
      window.addEventListener("scroll", this._scrollHandler, { passive: true });
      window.addEventListener("resize", this._scrollHandler);
      this._resizeObserver = new ResizeObserver(() => this._scheduleUpdate(true));
      for (const el of [nav, document.querySelector(".lumina-article"), document.querySelector("header")]) {
        if (el) this._resizeObserver.observe(el);
      }
    },

    _scheduleUpdate(measure = false) {
      this._needsMeasure ||= measure;
      if (this._rafId !== null) return;
      this._rafId = requestAnimationFrame(() => {
        this._rafId = null;
        if (this._needsMeasure) {
          this._computePositions();
          this._updateIndicator();
          this._needsMeasure = false;
        }
        this._updateCurrent();
      });
    },

    _updateCurrent() {
      // Use the same resolved offset as anchor navigation, including banners.
      const readingLine = parseFloat(getComputedStyle(this._links[0].target).scrollMarginTop) || 0;
      let current = this._links[0];
      for (const link of this._links) {
        if (link.target.getBoundingClientRect().top > readingLine + 1) break;
        current = link;
      }
      // Short final sections cannot always reach the reading line.
      if (window.scrollY > 0 && window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2) {
        current = this._links.at(-1);
      }
      if (this.activeId === current.id) return;
      this.activeId = current.id;
      this._updateActive();
      this._updateIndicator();
    },

    _computePositions() {
      this._positions.clear();
      let path = "";
      let previousX;
      for (const { id, el } of this._links) {
        const top = el.offsetTop;
        const bottom = top + el.offsetHeight;
        const x = el.offsetLeft + 1;
        this._positions.set(id, [top, bottom, x]);
        if (previousX === undefined) {
          path = `M ${x} ${top}`;
        } else if (x !== previousX) {
          // Round each step around the row boundary, including wrapped labels.
          path += ` L ${previousX} ${top - 8}`
            + ` C ${previousX} ${top}, ${x} ${top}, ${x} ${top + 8}`;
        }
        path += ` L ${x} ${bottom - 8}`;
        previousX = x;
      }
      const last = this._positions.get(this._links.at(-1).id);
      path += ` L ${last[2]} ${last[1]}`;
      for (const track of this._indicator.querySelectorAll("path")) {
        track.setAttribute("d", path);
      }
    },

    _updateActive() {
      for (const { id, el } of this._links) {
        el.classList.toggle("lumina-toc-active", id === this.activeId);
        if (id === this.activeId) el.setAttribute("aria-current", "location");
        else el.removeAttribute("aria-current");
      }
    },

    _updateIndicator() {
      if (!this._indicator || !this.activeId) return;
      const pos = this._positions.get(this.activeId);
      if (!pos) return;
      const [top, bottom, x] = pos;
      this._indicator.style.setProperty("--ind-top", `${top}px`);
      this._indicator.style.setProperty("--ind-bottom", `${bottom}px`);
      const dot = this._indicator.querySelector("circle");
      dot.setAttribute("cx", x);
      dot.setAttribute("cy", (top + bottom) / 2);
    },

    destroy() {
      window.removeEventListener("scroll", this._scrollHandler);
      window.removeEventListener("resize", this._scrollHandler);
      if (this._resizeObserver) this._resizeObserver.disconnect();
      if (this._rafId !== null) cancelAnimationFrame(this._rafId);
      if (this._indicator) this._indicator.remove();
    },
  };
}
