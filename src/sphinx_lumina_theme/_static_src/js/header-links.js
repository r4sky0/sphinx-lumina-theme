/**
 * @module header-links
 * @description Alpine.js component that converts section header permalink
 * clicks into a "copy link" action. Copies the full URL to the clipboard
 * and shows a brief "Copied!" tooltip.
 */

import { copyText } from "./utils/clipboard.js";

/**
 * Factory for the header-links Alpine component.
 * Registered as ``Alpine.data("headerLinks", headerLinks)``.
 *
 * **Methods:**
 *
 * - ``init()`` — Attaches click handlers to all ``.headerlink`` elements.
 *
 * @function headerLinks
 * @returns {object} Alpine.js component data.
 */
export default function headerLinks() {
  return {
    init() {
      document.querySelectorAll("a.headerlink").forEach((link) => {
        link.addEventListener("click", (e) => {
          e.preventDefault();
          const href = link.getAttribute("href");
          const url = new URL(href, window.location.href).toString();

          copyText(url)
            .then(() => {
              link.setAttribute("data-tooltip", "Copied!");
              link.classList.add("lumina-tooltip-visible");

              setTimeout(() => {
                link.classList.remove("lumina-tooltip-visible");
                setTimeout(() => link.removeAttribute("data-tooltip"), 150);
              }, 1500);
            })
            .catch((err) => {
              console.error("Lumina: failed to copy link", err);
            });
        });
      });
    },
  };
}
