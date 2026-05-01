/**
 * @module code-wrap
 * @description Injects a "wrap long lines" toggle button into every code
 * block (``div.highlight``) inside the article, alongside the existing
 * copy button. Click toggles ``data-lumina-wrap="on"`` on the code block;
 * CSS handles the visual wrap state.
 *
 * Disabled entirely when ``html[data-code-wrap]`` is absent (i.e., when
 * the ``code_wrap_toggle`` theme option is set to ``"false"``).
 */

const WRAP_ICON_SVG =
  '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" ' +
  'stroke="currentColor" stroke-width="2" stroke-linecap="round" ' +
  'stroke-linejoin="round" aria-hidden="true">' +
  '<path d="m16 16-3 3 3 3"/><path d="M3 12h14.5a1 1 0 0 1 0 7H13"/>' +
  '<path d="M3 19h6"/><path d="M3 5h18"/></svg>';

/**
 * Boot function that scans the page and injects a wrap-toggle button on
 * every code block. Called from ``boot()`` in app.js after ``Alpine.start()``.
 *
 * @function codeWrapToggle
 */
export default function codeWrapToggle() {
  if (!document.documentElement.hasAttribute("data-code-wrap")) return;
  const blocks = document.querySelectorAll(".lumina-article div.highlight");
  blocks.forEach(injectButton);
}

function injectButton(highlight) {
  if (highlight.querySelector(":scope > .lumina-wrap-toggle")) return;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "lumina-wrap-toggle";
  btn.setAttribute("aria-label", "Wrap long lines");
  btn.setAttribute("aria-pressed", "false");
  btn.title = "Wrap long lines";
  btn.insertAdjacentHTML("beforeend", WRAP_ICON_SVG);
  btn.addEventListener("click", () => toggle(highlight, btn));
  highlight.insertBefore(btn, highlight.firstChild);
}

function toggle(highlight, btn) {
  const on = highlight.getAttribute("data-lumina-wrap") === "on";
  if (on) {
    highlight.removeAttribute("data-lumina-wrap");
    btn.setAttribute("aria-pressed", "false");
    btn.setAttribute("aria-label", "Wrap long lines");
  } else {
    highlight.setAttribute("data-lumina-wrap", "on");
    btn.setAttribute("aria-pressed", "true");
    btn.setAttribute("aria-label", "Stop wrapping long lines");
  }
}
