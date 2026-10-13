/**
 * @module utils/reveal
 * @description Keeps a link visible inside its own scrolling panel, such as
 * the sidebar or the page TOC, without scrolling the page itself.
 */

/**
 * Center ``el`` in ``container`` when any part of it is out of view.
 * Hidden panels report empty boxes and are left alone.
 *
 * @param {HTMLElement|null} container — The scrolling panel.
 * @param {HTMLElement|null|undefined} el — A descendant to reveal.
 */
export function revealInContainer(container, el) {
  if (!container || !el) return;
  const box = container.getBoundingClientRect();
  const rect = el.getBoundingClientRect();
  if (rect.top >= box.top && rect.bottom <= box.bottom) return;
  container.scrollTop += rect.top - box.top - (box.height - rect.height) / 2;
}
