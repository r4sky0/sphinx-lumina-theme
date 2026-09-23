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
  const sig = dl.querySelector("dt.sig");
  if (!sig) return "/";
  const parts = [...sig.children].filter((el) =>
    el.matches(".sig-name, .sig-paren, .property, .sig-param"));
  return parts.slice(1).map((el) => el.textContent).join("").trim()
    .replace(/\((?:[^():]+:\s*)?([^()]+)\)/g, "{$1}") || "/";
}

/* Parse a field list section (e.g. "Request Headers") inside an endpoint's
   ``<dd>``. Returns name, type, value, and requiredness for list or paragraph entries. */
export function extractFieldSection(dd, label) {
  if (!dd) return [];
  const items = [];
  for (const dt of dd.querySelectorAll(":scope > dl.field-list > dt")) {
    if (!dt.textContent.replace(/:$/, "").trim().startsWith(label)) continue;

    const sibling = dt.nextElementSibling;
    if (!sibling) continue;

    for (const li of sibling.querySelectorAll(":scope > ul > li, :scope > p")) {
      const strong = li.querySelector("strong");
      if (!strong) continue;

      const name = strong.textContent.trim();
      const markers = li.querySelector("em")?.textContent.trim() ?? "string";
      const required = /\brequired\b/i.test(markers) || /\(required\)/i.test(li.textContent);
      const type = markers.replace(/,?\s*\brequired\b/i, "").trim();
      let value = "";

      if (label === "Request Headers") {
        const code = li.querySelector("code");
        if (code) {
          value = code.textContent;
        }
      }

      items.push({ name, type, value, required });
    }
  }
  return items;
}

export function fieldPlaceholder(type) {
  switch ((type || "").toLowerCase().split(/[:,\s]/)[0]) {
    case "integer": case "int": case "number": return 0;
    case "boolean": case "bool": return true;
    case "array": return [];
    case "object": return {};
    default: return "";
  }
}

/* Prefer the renderer's request example: it preserves nested objects and arrays.
   ponytail: DOM fields only provide a top-level fallback; use spec metadata if
   full schema reconstruction is needed. */
export function extractBody(dd) {
  for (const pre of dd.querySelectorAll(".highlight-http pre")) {
    const text = pre.textContent.trim();
    if (!/^(POST|PUT|PATCH|DELETE)\s/.test(text)) continue;
    const split = text.search(/\r?\n\r?\n/);
    if (split !== -1) return {
      body: text.slice(split).trim(),
      contentType: text.match(/^Content-Type:\s*(.+)$/im)?.[1].trim() || "application/json",
    };
  }
  const fields = extractFieldSection(dd, "Request JSON Object");
  const body = Object.fromEntries(fields.filter((f) => !/[.\[\]]/.test(f.name))
    .map((f) => [f.name, fieldPlaceholder(f.type)]));
  const contentType = extractFieldSection(dd, "Request Headers").find((h) => h.name.toLowerCase() === "content-type")?.value || "application/json";
  return { body: fields.length ? JSON.stringify(body, null, 2) : "", contentType };
}

/* One serializer for documented examples and the edited request. Quote every
   shell argument, including apostrophes, so copying never executes input. */
export function requestToCurl({ method, url, headers = {}, body }) {
  const quote = (value) => "'" + String(value).replace(/'/g, "'\\''") + "'";
  const parts = ["curl", "--globoff"];
  if (method === "HEAD") parts.push("--head");
  else if (method !== "GET") parts.push(`-X ${method}`);
  parts.push(quote(url));
  for (const [name, value] of Object.entries(headers)) parts.push(`-H ${quote(`${name}: ${value}`)}`);
  if (body !== undefined) parts.push(`--data-raw ${quote(body)}`);
  return parts.join(" \\\n  ");
}
