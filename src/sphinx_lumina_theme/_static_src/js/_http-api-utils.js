/**
 * @module _http-api-utils
 * @description Shared helpers for modules that parse ``dl.http`` endpoints
 * rendered by Sphinx's HTTP domain (try-it.js, curl-copy.js).
 */

const HTTP_METHODS = ["get", "post", "put", "patch", "delete", "head", "options"];

/* Walk up the ancestor chain for the nearest data-api-base-url override,
   falling back to the global value set by the theme option. */
export function resolveBaseUrl(el) {
  let node = el.parentElement;
  while (node && node !== document.documentElement) {
    if (node.dataset.apiBaseUrl !== undefined) return node.dataset.apiBaseUrl;
    node = node.parentElement;
  }
  return document.documentElement.dataset.apiBaseUrl || "";
}

export function extractMethod(dl) {
  for (const m of HTTP_METHODS) {
    if (dl.classList.contains(m)) return m.toUpperCase();
  }
  const first = dl.querySelector("dt.sig .sig-name.descname");
  return first ? first.textContent.trim() : "GET";
}

export function extractPath(dl) {
  const names = dl.querySelectorAll("dt.sig .sig-name.descname");
  return names.length >= 2 ? names[1].textContent.trim() : "/";
}

/* Parse a field list section (e.g. "Request Headers") inside an endpoint's
   ``<dd>``. Returns [{name, type, value}] for each ``<li>`` entry. */
export function extractFieldSection(dd, label) {
  if (!dd) return [];
  const fieldList = dd.querySelector("dl.field-list");
  if (!fieldList) return [];

  const items = [];
  for (const dt of fieldList.querySelectorAll(":scope > dt")) {
    if (!dt.textContent.replace(/:$/, "").trim().startsWith(label)) continue;

    const sibling = dt.nextElementSibling;
    if (!sibling) continue;

    for (const li of sibling.querySelectorAll("li")) {
      const strong = li.querySelector("strong");
      if (!strong) continue;

      const name = strong.textContent.trim();
      const type = li.querySelector("em")?.textContent.trim() ?? "string";
      let value = "";

      if (label === "Request Headers") {
        const code = li.querySelector("code");
        if (code) {
          value = code.textContent;
        } else {
          const dash = li.textContent.indexOf("\u2013");
          if (dash !== -1) value = li.textContent.slice(dash + 1).trim().replace(/\.$/, "");
        }
      }

      items.push({ name, type, value });
    }
  }
  return items;
}

export function fieldPlaceholder(type) {
  switch ((type || "").toLowerCase()) {
    case "integer": case "int": case "number": return 0;
    case "boolean": case "bool": return true;
    case "array": return [];
    case "object": return {};
    default: return "";
  }
}
