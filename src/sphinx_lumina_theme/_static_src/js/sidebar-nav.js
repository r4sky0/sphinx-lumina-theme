/**
 * @module sidebar-nav
 * @description Alpine.js component that makes the left sidebar toctree
 * collapsible. Walks the rendered ``<nav class="lumina-sidebar-nav">`` tree,
 * injects a chevron toggle button before every link that has a nested
 * ``<ul>``, and sets the initial open/closed state per branch:
 *
 * - Branches that contain the ``.current`` page are always expanded
 *   (auto-expand the current path).
 * - Branches whose ``<li>`` was tagged with ``data-nav-collapsed="true"``
 *   by the Python ``_mark_collapsed_entries`` helper start collapsed.
 * - Everything else starts expanded.
 *
 * State is recomputed on every page load — there is no ``localStorage``
 * persistence.
 */

const CHEVRON_SVG =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" ' +
  'fill="none" stroke="currentColor" stroke-width="2" ' +
  'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<path d="m9 18 6-6-6-6"/></svg>';

let _uid = 0;

/**
 * Factory for the sidebarNav Alpine component.
 * Registered as ``Alpine.data("sidebarNav", sidebarNav)`` and bound to the
 * ``<nav class="lumina-sidebar-nav">`` element via ``x-data``.
 *
 * @function sidebarNav
 * @returns {object} Alpine.js component data.
 */
export default function sidebarNav() {
  return {
    init() {
      const nav = this.$el;
      if (!nav) return;

      const branches = nav.querySelectorAll("li");
      branches.forEach((li) => {
        const nestedList = this._directChildUl(li);
        if (!nestedList) return;

        const link = li.querySelector(":scope > a");
        if (!link) return;

        // Give the nested list a stable id so aria-controls can reference it.
        if (!nestedList.id) {
          _uid += 1;
          nestedList.id = `lumina-nav-branch-${_uid}`;
        }

        // Build and insert the toggle button before the link.
        const button = document.createElement("button");
        button.type = "button";
        button.className = "lumina-sidebar-nav-toggle";
        button.setAttribute("aria-controls", nestedList.id);
        button.setAttribute(
          "aria-label",
          `Toggle ${link.textContent.trim()}`,
        );
        button.innerHTML = CHEVRON_SVG;
        button.addEventListener("click", (event) => {
          event.preventDefault();
          event.stopPropagation();
          this._toggle(li, button);
        });
        li.insertBefore(button, link.nextSibling);

        // Mark the li so CSS can style branches specifically.
        li.classList.add("has-children");

        // Determine initial state.  Auto-expand if the current page is
        // inside this branch, otherwise honor the server-side opt-in.
        const hasCurrent = li.querySelector(".current") !== null ||
          li.classList.contains("current");
        const optCollapsed = li.dataset.navCollapsed === "true";

        if (!hasCurrent && optCollapsed) {
          li.classList.add("is-collapsed");
          button.setAttribute("aria-expanded", "false");
        } else {
          button.setAttribute("aria-expanded", "true");
        }
      });
    },

    /**
     * Return the direct-child ``<ul>`` of an ``<li>``, or ``null``.
     * @param {HTMLElement} li
     * @returns {HTMLUListElement|null}
     */
    _directChildUl(li) {
      for (const child of li.children) {
        if (child.tagName === "UL") return child;
      }
      return null;
    },

    /**
     * Toggle a branch open/closed and update ``aria-expanded``.
     * @param {HTMLElement} li
     * @param {HTMLButtonElement} button
     */
    _toggle(li, button) {
      const collapsed = li.classList.toggle("is-collapsed");
      button.setAttribute("aria-expanded", String(!collapsed));
    },
  };
}
