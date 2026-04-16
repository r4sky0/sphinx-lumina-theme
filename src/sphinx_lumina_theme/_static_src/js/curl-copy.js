/**
 * @module curl-copy
 * @description Scans HTTP-domain endpoints (``dl.http``) and injects a
 * "Copy as curl" button into each signature card. Builds the curl command
 * from the rendered method, path, query parameters, headers, and JSON body
 * fields in the DOM. The base URL comes from the ``api_base_url`` theme option.
 *
 * Exports two items:
 * - {@link curlCopyBtn} — Alpine.data factory, registered in app.js.
 * - {@link curlCopy} — boot function, called from ``boot()`` in app.js.
 */

import {
  resolveBaseUrl,
  extractMethod,
  extractPath,
  extractFieldSection,
  fieldPlaceholder,
} from "./_http-api-utils.js";

/* Module-level store — maps each injected button to its curl string */
const _curlCmds = new WeakMap();

/* ── Alpine.data factory ───────────────────────────────────────────── */

/**
 * Alpine.js data factory for the per-endpoint copy-curl button.
 * Registered as ``Alpine.data("curlCopyBtn", curlCopyBtn)``.
 *
 * **Properties:**
 *
 * - ``copied`` *(boolean)* — Briefly ``true`` after a successful copy.
 *
 * **Methods:**
 *
 * - ``copy()`` — Copies the pre-built curl command to the clipboard.
 *
 * @function curlCopyBtn
 * @returns {object} Alpine.js component data.
 */
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

/**
 * Boot function that scans the page for HTTP endpoints and injects
 * copy-curl buttons. Called from ``boot()`` in app.js after ``Alpine.start()``.
 *
 * @function curlCopy
 */
export default function curlCopy() {
  const endpoints = document.querySelectorAll("dl.http");
  if (endpoints.length === 0) return;

  endpoints.forEach((dl) => {
    injectButton(dl, resolveBaseUrl(dl));
  });
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
  btn.setAttribute("x-on:click", "copy()");
  btn.setAttribute("x-bind:class", "{ 'is-copied': copied }");
  btn.setAttribute("x-bind:aria-label", "copied ? 'Copied!' : 'Copy as curl'");
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
      body[f.name] = fieldPlaceholder(f.type);
    }
    parts.push(`-d '${JSON.stringify(body)}'`);
  }

  if (parts.length <= 2) {
    return parts.join(" ");
  }
  return parts.join(" \\\n  ");
}

/* ── DOM extraction helpers ────────────────────────────────────────── */

function extractHeaders(dl) {
  return extractFieldSection(dl.querySelector("dd"), "Request Headers");
}

function extractQueryParams(dl) {
  return extractFieldSection(dl.querySelector("dd"), "Query Parameters").map((i) => i.name);
}

function extractJsonFields(dl) {
  return extractFieldSection(dl.querySelector("dd"), "Request JSON Object");
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
