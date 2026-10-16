/**
 * @module utils/i18n
 * @description Translation lookup for strings rendered by JavaScript. The
 * ``components/i18n.html`` template emits ``#lumina-i18n`` with the
 * translated catalog for non-English builds; English builds omit it and every
 * lookup falls back to its key.
 */

let catalog;

/**
 * Translate an English UI string.
 *
 * @param {string} key — English source string; must be listed in ``components/i18n.html``.
 * @param {Object<string, *>} [vars] — Values for ``{name}`` placeholders.
 * @returns {string} The translation, or ``key`` when none is available.
 */
export function t(key, vars = {}) {
  if (catalog === undefined) {
    try {
      catalog = JSON.parse(document.getElementById("lumina-i18n")?.textContent || "{}");
    } catch {
      catalog = {};
    }
  }
  return (catalog[key] || key).replace(/\{(\w+)\}/g, (match, name) => (name in vars ? vars[name] : match));
}
