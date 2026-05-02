/**
 * @module image-lightbox
 * @description Alpine.js component that adds click-to-zoom for ``<img>``
 * elements inside the article. On init it scans ``.lumina-article`` for
 * images, tags them as zoomable, and binds click/keyboard handlers. Any
 * other element (e.g. a custom inline ``<svg>``) can opt in by adding
 * the ``data-lumina-zoom`` attribute.
 *
 * Skips elements with ``no-lightbox`` / ``data-no-lightbox`` opt-outs and
 * any element with the ``lumina-icon`` class. Mermaid diagrams are
 * intentionally **not** auto-tagged: ``sphinxcontrib-mermaid`` already
 * ships a fullscreen viewer with pan and zoom that's better suited to
 * complex diagrams than a single fixed-size overlay, and Lumina's
 * Mermaid theming relies on selectors (``.lumina-article .mermaid …``)
 * that wouldn't match inside the cloned overlay.
 *
 * Disabled entirely when ``html[data-lightbox]`` is absent.
 */

/**
 * Alpine.js data factory for the lightbox overlay.
 * Registered as ``Alpine.data("imageLightbox", imageLightbox)``.
 *
 * **Properties:**
 *
 * - ``isOpen`` *(boolean)* — Whether the overlay is currently visible.
 * - ``contentType`` *(string)* — ``"img"`` or ``"svg"``.
 * - ``imgSrc`` / ``imgAlt`` *(string)* — Source and alt for ``<img>`` mode.
 * - ``caption`` *(string)* — Caption text shown beneath the figure.
 *
 * **Methods:**
 *
 * - ``init()`` — Tags zoomable elements and attaches handlers.
 * - ``open(el)`` — Show the overlay with content from ``el``.
 * - ``close()`` — Hide the overlay and restore focus.
 *
 * @function imageLightbox
 * @returns {object} Alpine.js component data.
 */
export default function imageLightbox() {
  return {
    isOpen: false,
    contentType: "img",
    imgSrc: "",
    imgAlt: "",
    caption: "",
    _trigger: null,

    init() {
      if (!document.documentElement.hasAttribute("data-lightbox")) return;
      const article = document.querySelector(".lumina-article");
      if (!article) return;

      article.querySelectorAll("img").forEach((el) => this._tag(el));
      article
        .querySelectorAll("[data-lumina-zoom]")
        .forEach((el) => this._tag(el));

      // Move focus to the close button each time the overlay opens.
      // $watch fires after Alpine flushes the reactive DOM update.
      this.$watch("isOpen", (open) => {
        if (open) {
          requestAnimationFrame(() => {
            const btn = this.$el.querySelector(".lumina-lightbox-close");
            if (btn) btn.focus();
          });
        }
      });
    },

    _shouldSkipElement(el) {
      if (el.classList.contains("no-lightbox")) return true;
      if (el.hasAttribute("data-no-lightbox")) return true;
      if (el.classList.contains("lumina-icon")) return true;
      return false;
    },

    _isAutoWrapAnchor(anchor, img) {
      // Sphinx auto-wraps image/figure directives in an <a> linking to
      // the image source; Lumina takes over that click with the overlay.
      if (!anchor) return false;
      if (anchor.classList.contains("image-reference")) return true;
      if (anchor.href && anchor.href === img.src) return true;
      return false;
    },

    _tag(el) {
      if (el.classList.contains("lumina-zoomable")) return;
      if (this._shouldSkipElement(el)) return;

      // For <img> inside <a>: route through the anchor when it's a
      // Sphinx auto-wrap; skip when it's a user-defined link.
      if (el.tagName.toLowerCase() === "img") {
        const anchor = el.closest("a");
        if (anchor) {
          if (this._isAutoWrapAnchor(anchor, el)) {
            this._tagAnchor(anchor, el);
            return;
          }
          return; // user-defined link — leave alone
        }
      }

      el.classList.add("lumina-zoomable");
      el.setAttribute("role", "button");
      el.setAttribute("tabindex", "0");

      // iOS Safari only synthesizes a `click` from a tap when the element is
      // naturally clickable, has `cursor: pointer`, or has an `onclick`
      // property set. `addEventListener("click", ...)` alone is silently
      // dropped on tap, so assign via the property here.
      el.onclick = () => this.open(el);
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          this.open(el);
        }
      });
    },

    _tagAnchor(anchor, img) {
      if (anchor.classList.contains("lumina-zoomable")) return;
      anchor.classList.add("lumina-zoomable");

      const open = (e) => {
        e.preventDefault();
        this.open(img, anchor);
      };

      // Anchor handles keyboard activation (Enter/Space → native click) and
      // desktop mouse clicks.
      anchor.onclick = open;

      // On iOS Safari the tap target is the inner <img> — and Sphinx
      // auto-wraps a bare image with no surrounding text, so the anchor
      // never sees the touch. iOS only synthesizes a click for an element
      // that's naturally clickable / has cursor:pointer / has an onclick
      // property; mirror onclick onto the img and stop propagation so we
      // don't double-fire when the click bubbles back up to the anchor.
      img.onclick = (e) => {
        e.stopPropagation();
        open(e);
      };
    },

    _bestSrc(img) {
      const srcset = img.getAttribute("srcset");
      if (srcset) {
        const candidates = srcset
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean);
        if (candidates.length) {
          // Take the last candidate's URL (typically the largest).
          const last = candidates[candidates.length - 1].split(/\s+/)[0];
          if (last) return last;
        }
      }
      return img.currentSrc || img.src;
    },

    _resolveCaption(el) {
      const figure = el.closest("figure");
      if (figure) {
        const fc = figure.querySelector("figcaption");
        if (fc && fc.textContent.trim()) return fc.textContent.trim();
      }
      if (el.tagName.toLowerCase() === "svg") {
        const title = el.querySelector(":scope > title, :scope > desc");
        if (title && title.textContent.trim()) {
          return title.textContent.trim();
        }
      }
      const aria = el.getAttribute("aria-label");
      if (aria && aria.trim()) return aria.trim();
      const alt = el.getAttribute("alt") || el.getAttribute("title");
      if (alt && alt.trim()) return alt.trim();
      return "";
    },

    open(el, trigger) {
      // ``trigger`` is the focusable element to restore on close — falls
      // back to the displayed element when called without an explicit one.
      this._trigger = trigger || el;
      this.caption = this._resolveCaption(el);

      if (el.tagName.toLowerCase() === "img") {
        this.contentType = "img";
        this.imgSrc = this._bestSrc(el);
        this.imgAlt = el.getAttribute("alt") || "";
      } else {
        this.contentType = "svg";
        const host = this.$el.querySelector(".lumina-lightbox-svg-host");
        if (host) {
          host.replaceChildren();
          const clone = el.cloneNode(true);
          clone.removeAttribute("width");
          clone.removeAttribute("height");
          clone.removeAttribute("style");
          clone.style.maxWidth = "100%";
          clone.style.maxHeight = "100%";
          clone.style.height = "auto";
          host.appendChild(clone);
        }
      }

      this.isOpen = true;
      document.body.classList.add("lumina-lightbox-open");
      // Focus is moved to the close button by the $watch handler in init().
    },

    close() {
      this.isOpen = false;
      document.body.classList.remove("lumina-lightbox-open");
      const host = this.$el.querySelector(".lumina-lightbox-svg-host");
      if (host) host.replaceChildren();
      if (this._trigger) {
        const trigger = this._trigger;
        this._trigger = null;
        // Restore focus after the close transition starts so the trigger
        // is back on screen first.
        this.$nextTick(() => trigger.focus({ preventScroll: false }));
      }
    },
  };
}
