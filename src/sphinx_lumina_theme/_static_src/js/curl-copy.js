/**
 * Curl Copy
 *
 * Scans HTTP domain endpoints (dl.http) and injects a "Copy curl"
 * button (Alpine.js component) into each signature card. Builds the
 * curl command from the rendered method, path, query parameters,
 * headers, and JSON body fields in the DOM.
 *
 * Exports:
 *   curlCopyBtn  — Alpine.data factory, registered in app.js
 *   curlCopy     — boot function, called from boot() in app.js
 *
 * Called from boot() in app.js after Alpine.start().
 * The base URL is read from html_theme_options["api_base_url"],
 * output as a data attribute on <html> by the theme template.
 */

/* Module-level store — maps each injected button to its curl string */
const _curlCmds = new WeakMap();

/* ── Alpine.data factory ───────────────────────────────────────────── */

export function curlCopyBtn() {
  return {
    copied: false,

    async copy() {
      const curl = _curlCmds.get(this.$el);
      if (!curl) return;
      try {
        await copyText(curl);
      } catch {
        return;
      }
      this.copied = true;
      setTimeout(() => { this.copied = false; }, 1500);
    },
  };
}

/* ── Boot ──────────────────────────────────────────────────────────── */

export default function curlCopy() {
  const endpoints = document.querySelectorAll("dl.http");
  if (endpoints.length === 0) return;

  endpoints.forEach((dl) => {
    injectButton(dl, resolveBaseUrl(dl));
  });
}

/* Walk up the ancestor chain for the nearest data-api-base-url override,
   falling back to the global value set by the theme option. */
function resolveBaseUrl(el) {
  let node = el.parentElement;
  while (node && node !== document.documentElement) {
    if (node.dataset.apiBaseUrl !== undefined) return node.dataset.apiBaseUrl;
    node = node.parentElement;
  }
  return document.documentElement.dataset.apiBaseUrl || "";
}

/* ── Button injection ──────────────────────────────────────────────── */

function injectButton(dl, baseUrl) {
  const sig = dl.querySelector("dt.sig");
  if (!sig) return;

  if (baseUrl) {
    let host = baseUrl.replace(/\/$/, "");
    try { host = new URL(baseUrl).hostname; } catch {}
    const tag = document.createElement("span");
    tag.className = "lumina-api-host";
    tag.textContent = host;
    sig.appendChild(tag);
  }

  const curl = buildCurl(dl, baseUrl);

  const btn = document.createElement("button");
  btn.className = "lumina-curl-copy";
  btn.setAttribute("x-data", "curlCopyBtn");
  btn.setAttribute("@click", "copy()");
  btn.setAttribute(":class", "{ 'is-copied': copied }");
  btn.setAttribute(":aria-label", "copied ? 'Copied!' : 'Copy as curl'");
  btn.setAttribute("title", "Copy as curl");
  btn.setAttribute("aria-label", "Copy as curl");

  _curlCmds.set(btn, curl);

  /* Two SVGs — Alpine's x-show toggles between them */
  btn.insertAdjacentHTML("beforeend", `
    <svg x-show="!copied" width="14" height="14" viewBox="0 0 24 24" fill="none"
         stroke="currentColor" stroke-width="2" stroke-linecap="round"
         stroke-linejoin="round" aria-hidden="true">
      <polyline points="16 18 22 12 16 6"/>
      <polyline points="8 6 2 12 8 18"/>
    </svg>
    <svg x-show="copied" width="14" height="14" viewBox="0 0 24 24" fill="none"
         stroke="currentColor" stroke-width="2" stroke-linecap="round"
         stroke-linejoin="round" aria-hidden="true">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  `);

  sig.appendChild(btn);
  window.Alpine.initTree(btn);
}

/* ── Curl command builder ── */

function buildCurl(dl, baseUrl) {
  const method = extractMethod(dl);
  const path = extractPath(dl);
  const url = baseUrl ? baseUrl.replace(/\/$/, "") + path : path;
  const headers = extractHeaders(dl);
  const jsonFields = extractJsonFields(dl);
  const queryParams = extractQueryParams(dl);

  const parts = ["curl"];

  if (method !== "GET") {
    parts.push(`-X ${method}`);
  }

  let fullUrl = url;
  if (queryParams.length > 0) {
    const qs = queryParams.map((p) => `${p}=<value>`).join("&");
    fullUrl += `?${qs}`;
  }
  parts.push(`"${fullUrl}"`);

  for (const h of headers) {
    if (h.name.toLowerCase() === "content-type" && jsonFields.length > 0) {
      continue;
    }
    parts.push(`-H "${h.name}: ${h.value}"`);
  }

  if (jsonFields.length > 0) {
    parts.push('-H "Content-Type: application/json"');
    const body = {};
    for (const f of jsonFields) {
      body[f.name] = placeholder(f.type);
    }
    parts.push(`-d '${JSON.stringify(body)}'`);
  }

  if (parts.length <= 2) {
    return parts.join(" ");
  }
  return parts.join(" \\\n  ");
}

/* ── DOM extraction helpers ────────────────────────────────────────── */

function extractMethod(dl) {
  const methods = ["get", "post", "put", "patch", "delete", "head", "options"];
  for (const m of methods) {
    if (dl.classList.contains(m)) return m.toUpperCase();
  }
  const first = dl.querySelector("dt.sig .sig-name.descname");
  return first ? first.textContent.trim() : "GET";
}

function extractPath(dl) {
  const names = dl.querySelectorAll("dt.sig .sig-name.descname");
  return names.length >= 2 ? names[1].textContent.trim() : "/";
}

function extractHeaders(dl) {
  return extractFieldSection(dl, "Request Headers");
}

function extractQueryParams(dl) {
  return extractFieldSection(dl, "Query Parameters").map((i) => i.name);
}

function extractJsonFields(dl) {
  return extractFieldSection(dl, "Request JSON Object");
}

function extractFieldSection(dl, label) {
  const dd = dl.querySelector("dd");
  if (!dd) return [];

  const fieldList = dd.querySelector("dl.field-list");
  if (!fieldList) return [];

  const items = [];

  for (const dt of fieldList.querySelectorAll(":scope > dt")) {
    if (!dt.textContent.replace(/:$/, "").trim().startsWith(label)) continue;

    const fieldDd = dt.nextElementSibling;
    if (!fieldDd || fieldDd.tagName.toLowerCase() !== "dd") continue;

    for (const li of fieldDd.querySelectorAll("li")) {
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
          const text = li.textContent;
          const dash = text.indexOf("\u2013");
          if (dash !== -1) value = text.slice(dash + 1).trim().replace(/\.$/, "");
        }
      }

      items.push({ name, type, value });
    }
  }

  return items;
}

function placeholder(type) {
  switch ((type || "").toLowerCase()) {
    case "integer": case "int": case "number": return 0;
    case "boolean": case "bool": return true;
    case "array": return [];
    case "object": return {};
    default: return "";
  }
}

/* ── Clipboard ─────────────────────────────────────────────────────── */

function copyText(text) {
  if (navigator.clipboard) {
    return navigator.clipboard.writeText(text);
  }
  /* Fallback for older browsers */
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.cssText = "position:fixed;opacity:0";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
  return Promise.resolve();
}
