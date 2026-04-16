/**
 * @module try-it
 * @description Injects an interactive "Try It Out" request panel into each
 * HTTP-domain endpoint (``dl.http``). Extracts parameters from the rendered
 * DOM and sends real ``fetch`` requests. Bearer tokens are persisted in
 * ``sessionStorage`` (key ``lumina-api-token``).
 *
 * Exports two items:
 * - {@link tryItPanel} — Alpine.data factory, registered in app.js.
 * - {@link tryIt} — boot function, called from ``boot()`` in app.js.
 */

import {
  resolveBaseUrl,
  extractMethod,
  extractPath,
  extractFieldSection,
  fieldPlaceholder,
} from "./_http-api-utils.js";

const SESSION_KEY = "lumina-api-token";

/* Module-level config store — keyed by the injected wrapper element */
const _configs = new WeakMap();

/* ── Alpine.data factory ───────────────────────────────────────────── */

/**
 * Alpine.js data factory for the interactive request panel.
 * Registered as ``Alpine.data("tryItPanel", tryItPanel)``.
 *
 * **Properties:**
 *
 * - ``open`` *(boolean)* — Whether the panel is expanded.
 * - ``sending`` *(boolean)* — True while a request is in-flight.
 * - ``response`` *(object|null)* — Last response (status, body, elapsed time).
 * - ``method`` *(string)* — HTTP method (GET, POST, etc.).
 * - ``path`` *(string)* — Endpoint path with ``{param}`` placeholders.
 * - ``baseUrl`` *(string)* — API base URL from theme options.
 *
 * **Methods:**
 *
 * - ``init()`` — Reads config injected by the boot function.
 * - ``send()`` — Sends the request and populates the response.
 * - ``copyResponse()`` — Copies the response body to the clipboard.
 * - ``clear()`` — Resets the response and error state.
 *
 * @function tryItPanel
 * @returns {object} Alpine.js component data.
 */
export function tryItPanel() {
  return {
    /* Panel state */
    open: false,
    sending: false,
    response: null,
    showBearer: false,
    copiedResponse: false,

    /* Form values */
    bearerToken: "",
    pathValues: {},
    queryValues: {},
    headerValues: {},
    bodyJson: "{}",
    bodyError: null,

    /* Config — populated in init() from _configs */
    method: "GET",
    path: "/",
    baseUrl: "",
    pathParams: [],
    queryParams: [],
    allHeaders: [],
    bodyFields: [],
    hasBody: false,
    needsAuth: false,
    extraHeaders: [],

    init() {
      const cfg = _configs.get(this.$el);
      if (!cfg) return;
      Object.assign(this, cfg);

      /* Default body from extracted fields */
      if (this.hasBody) {
        if (this.bodyFields.length) {
          const obj = {};
          this.bodyFields.forEach((f) => { obj[f.name] = fieldPlaceholder(f.type); });
          this.bodyJson = JSON.stringify(obj, null, 2);
        } else {
          this.bodyJson = "{}";
        }
      }

      this.bearerToken = sessionStorage.getItem(SESSION_KEY) || "";
      this.needsAuth = this.allHeaders.some((h) => h.name.toLowerCase() === "authorization");
      this.extraHeaders = this.allHeaders.filter(
        (h) => !["authorization", "content-type"].includes(h.name.toLowerCase()),
      );
    },

    /* Computed URL — reactive to form changes */
    get computedUrl() {
      let resolved = this.path;
      this.pathParams.forEach((p) => {
        const val = (this.pathValues[p.name] || "").trim();
        resolved = resolved.replace(`{${p.name}}`, val ? encodeURIComponent(val) : `{${p.name}}`);
      });

      const qps = this.queryParams
        .filter((p) => (this.queryValues[p.name] || "").trim())
        .map((p) => `${encodeURIComponent(p.name)}=${encodeURIComponent(this.queryValues[p.name])}`);

      const base = this.baseUrl ? this.baseUrl.replace(/\/$/, "") : "";
      return base + resolved + (qps.length ? "?" + qps.join("&") : "");
    },

    /* Syntax-highlighted or escaped response body */
    get formattedBody() {
      if (!this.response) return "";
      return this.response.isJson ? this.response.bodyHtml : esc(this.response.bodyText);
    },

    /* ── Send ──────────────────────────────────────────────────────── */

    async send() {
      const headers = {};

      if (this.needsAuth && this.bearerToken.trim()) {
        headers["Authorization"] = `Bearer ${this.bearerToken.trim()}`;
        sessionStorage.setItem(SESSION_KEY, this.bearerToken.trim());
      }

      this.extraHeaders.forEach((h) => {
        const val = (this.headerValues[h.name] || "").trim();
        if (val) headers[h.name] = val;
      });

      let body;
      if (this.hasBody && this.bodyJson.trim()) {
        try {
          JSON.parse(this.bodyJson);
          this.bodyError = null;
        } catch {
          this.bodyError = "Request body is not valid JSON.";
          return;
        }
        body = this.bodyJson;
        headers["Content-Type"] = "application/json";
      }

      this.sending = true;
      this.response = null;

      const t0 = performance.now();
      try {
        const res     = await fetch(this.computedUrl, { method: this.method, headers, body, credentials: "omit" });
        const elapsed = Math.round(performance.now() - t0);
        const ct      = res.headers.get("content-type") || "";
        const isJson  = ct.includes("json");

        /* Handle empty-body responses (e.g. 204 No Content) */
        let raw = "";
        let resolvedIsJson = isJson;
        if (res.status !== 204) {
          try {
            raw = isJson ? JSON.stringify(await res.json(), null, 2) : await res.text();
          } catch {
            raw = "";
            resolvedIsJson = false;
          }
        }
        const bodyText = raw.trim() || "(No response body)";

        this.response = {
          status:     res.status,
          statusText: res.statusText,
          statusClass: res.status >= 500 ? "error" : res.status >= 400 ? "warning" : res.status >= 300 ? "info" : "success",
          elapsed,
          bodyText,
          bodyHtml: resolvedIsJson && raw.trim() ? highlight(raw) : null,
          isJson:   resolvedIsJson && raw.trim() ? true : false,
          error:    false,
        };
      } catch (err) {
        const elapsed = Math.round(performance.now() - t0);
        this.response = {
          status:     null,
          statusText: "Error",
          statusClass: "error",
          elapsed,
          bodyText: err.name === "TypeError"
            ? `Network error — this may be a CORS restriction.\n\n${err.message}`
            : err.message,
          bodyHtml: null,
          isJson:  false,
          error:   true,
        };
      } finally {
        this.sending = false;
      }
    },

    async copyResponse() {
      const text = this.response?.bodyText;
      if (!text || text === "(No response body)") return;
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        return;
      }
      this.copiedResponse = true;
      setTimeout(() => { this.copiedResponse = false; }, 1500);
    },

    clear() {
      this.response  = null;
      this.bodyError = null;
    },
  };
}

/* ── Boot ──────────────────────────────────────────────────────────── */

/**
 * Boot function that scans the page for HTTP endpoints and injects
 * interactive "Try It Out" panels. Called from ``boot()`` in app.js
 * after ``Alpine.start()``. Skipped if ``data-try-it-out="false"``
 * is set on ``<html>``.
 *
 * @function tryIt
 */
export default function tryIt() {
  if (document.documentElement.dataset.tryItOut === "false") return;
  const endpoints = document.querySelectorAll("dl.http");
  if (!endpoints.length) return;

  endpoints.forEach((dl) => {
    const baseUrl = resolveBaseUrl(dl);
    if (baseUrl) injectPanel(dl, baseUrl);
  });
}

/* ── Panel injection ───────────────────────────────────────────────── */

function injectPanel(dl, baseUrl) {
  const dd = dl.querySelector(":scope > dd");
  if (!dd) return;

  const method      = extractMethod(dl);
  const path        = extractPath(dl);
  const pathParams  = parsePathParams(path);
  const queryParams = extractFieldSection(dd, "Query Parameters");
  const allHeaders  = extractFieldSection(dd, "Request Headers");
  const bodyFields  = extractFieldSection(dd, "Request JSON Object");
  const hasBody     = ["POST", "PUT", "PATCH"].includes(method);

  /* Wrapper is the Alpine component root */
  const wrap = document.createElement("div");
  wrap.className = "lumina-try-it";
  wrap.setAttribute("x-data", "tryItPanel");

  /* Store config for Alpine init() to read via this.$el */
  _configs.set(wrap, { method, path, baseUrl, pathParams, queryParams, allHeaders, bodyFields, hasBody });

  /* Static Alpine template */
  wrap.insertAdjacentHTML("beforeend", PANEL_TEMPLATE);

  dd.appendChild(wrap);

  /* Initialize Alpine on the injected subtree */
  window.Alpine.initTree(wrap);
}

/* ── Alpine template ───────────────────────────────────────────────── */

const PANEL_TEMPLATE = `
  <button type="button" class="lumina-try-it-toggle"
          @click="open = !open"
          :class="{ 'is-open': open }"
          :aria-expanded="open.toString()">
    <svg class="lumina-try-it-chevron" width="10" height="10" viewBox="0 0 24 24"
         fill="none" stroke="currentColor" stroke-width="2.5"
         stroke-linecap="round" stroke-linejoin="round"
         :class="{ 'is-open': open }" aria-hidden="true">
      <polyline points="9 18 15 12 9 6"/>
    </svg>
    Try it out
  </button>

  <div class="lumina-try-it-grid" :class="{ 'is-open': open }">
    <div class="lumina-try-it-panel">

      <div class="lumina-try-it-url-bar">
        <span class="lumina-try-it-method-pill"
              :class="\`lumina-try-it-method-pill--\${method.toLowerCase()}\`"
              x-text="method"></span>
        <code class="lumina-try-it-url-display" x-text="computedUrl"></code>
      </div>

      <div class="lumina-try-it-section" x-show="pathParams.length">
        <div class="lumina-try-it-section-label">Path Parameters</div>
        <template x-for="p in pathParams" :key="p.name">
          <div class="lumina-try-it-param-row">
            <label class="lumina-try-it-param-name" :for="\`lumina-path-\${p.name}\`">
              <span x-text="p.name"></span>
              <span class="lumina-try-it-required" aria-label="required">*</span>
            </label>
            <input class="lumina-try-it-input"
                   :id="\`lumina-path-\${p.name}\`"
                   x-model="pathValues[p.name]"
                   :placeholder="p.name"
                   type="text" autocomplete="off" spellcheck="false" />
          </div>
        </template>
      </div>

      <div class="lumina-try-it-section" x-show="queryParams.length">
        <div class="lumina-try-it-section-label">Query Parameters</div>
        <template x-for="p in queryParams" :key="p.name">
          <div class="lumina-try-it-param-row">
            <label class="lumina-try-it-param-name" :for="\`lumina-query-\${p.name}\`">
              <span x-text="p.name"></span>
              <span class="lumina-try-it-type-tag" x-text="p.type" x-show="p.type"></span>
            </label>
            <input class="lumina-try-it-input"
                   :id="\`lumina-query-\${p.name}\`"
                   x-model="queryValues[p.name]"
                   placeholder="optional"
                   type="text" autocomplete="off" spellcheck="false" />
          </div>
        </template>
      </div>

      <div class="lumina-try-it-section" x-show="needsAuth">
        <div class="lumina-try-it-section-label">Authorization</div>
        <div class="lumina-try-it-param-row">
          <label class="lumina-try-it-param-name" for="lumina-bearer-token">Bearer Token</label>
          <div class="lumina-try-it-bearer-wrap">
            <span class="lumina-try-it-bearer-prefix">Bearer</span>
            <input class="lumina-try-it-input"
                   id="lumina-bearer-token"
                   x-model="bearerToken"
                   :type="showBearer ? 'text' : 'password'"
                   placeholder="your-token"
                   autocomplete="off" spellcheck="false" />
            <button type="button" class="lumina-try-it-eye-toggle"
                    @click="showBearer = !showBearer"
                    :aria-label="showBearer ? 'Hide token' : 'Show token'">
              <svg x-show="!showBearer" width="14" height="14" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" stroke-width="2" stroke-linecap="round"
                   stroke-linejoin="round" aria-hidden="true">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg x-show="showBearer" width="14" height="14" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" stroke-width="2" stroke-linecap="round"
                   stroke-linejoin="round" aria-hidden="true">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div class="lumina-try-it-section" x-show="extraHeaders.length">
        <div class="lumina-try-it-section-label">Headers</div>
        <template x-for="h in extraHeaders" :key="h.name">
          <div class="lumina-try-it-param-row">
            <label class="lumina-try-it-param-name" :for="\`lumina-header-\${h.name}\`" x-text="h.name"></label>
            <input class="lumina-try-it-input"
                   :id="\`lumina-header-\${h.name}\`"
                   x-model="headerValues[h.name]"
                   :placeholder="h.value || h.name"
                   type="text" autocomplete="off" spellcheck="false" />
          </div>
        </template>
      </div>

      <div class="lumina-try-it-section" x-show="hasBody">
        <div class="lumina-try-it-section-label">
          Request Body <span class="lumina-try-it-type-tag">JSON</span>
        </div>
        <textarea class="lumina-try-it-body"
                  x-model="bodyJson"
                  :class="{ 'has-error': bodyError }"
                  rows="5" spellcheck="false" autocomplete="off"
                  placeholder="{}"></textarea>
        <p class="lumina-try-it-body-error" x-show="bodyError" x-text="bodyError"></p>
      </div>

      <div class="lumina-try-it-actions">
        <button type="button" class="lumina-try-it-send"
                @click="send()"
                :disabled="sending"
                :class="{ 'is-loading': sending }"
                :aria-label="sending ? 'Sending request\u2026' : 'Send request'">
          <svg class="lumina-send-icon" width="12" height="12" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" stroke-width="2.5" stroke-linecap="round"
               stroke-linejoin="round" aria-hidden="true">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
          <svg class="lumina-send-spinner" width="12" height="12" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" stroke-width="2.5" stroke-linecap="round"
               stroke-linejoin="round" aria-hidden="true">
            <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
          </svg>
          <span x-text="sending ? 'Sending\u2026' : 'Send Request'"></span>
        </button>
        <button type="button" class="lumina-try-it-clear"
                @click="clear()" x-show="response">Clear</button>
      </div>

      <div class="lumina-try-it-response" x-show="response || sending" x-cloak>
        <div class="lumina-try-it-sending" x-show="sending">Sending\u2026</div>
        <template x-if="response && !sending">
          <div>
            <div class="lumina-try-it-res-header">
              <span class="lumina-try-it-status"
                    :class="\`lumina-try-it-status--\${response.statusClass}\`"
                    x-text="response.status ? response.status + ' ' + response.statusText : response.statusText">
              </span>
              <span class="lumina-try-it-elapsed" x-text="response.elapsed + 'ms'"></span>
              <button type="button" class="lumina-try-it-copy-res"
                      @click="copyResponse()"
                      :class="{ 'is-copied': copiedResponse }"
                      :aria-label="copiedResponse ? 'Copied!' : 'Copy response'"
                      x-show="response.bodyText !== '(No response body)'">
                <svg x-show="!copiedResponse" width="13" height="13" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="2" stroke-linecap="round"
                     stroke-linejoin="round" aria-hidden="true">
                  <rect x="9" y="9" width="13" height="13" rx="2"/>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
                <svg x-show="copiedResponse" width="13" height="13" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="2" stroke-linecap="round"
                     stroke-linejoin="round" aria-hidden="true">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </button>
            </div>
            <pre class="lumina-try-it-res-body"
                 :class="{ 'lumina-try-it-res-body--error': response.error }"><code x-html="formattedBody"></code></pre>
          </div>
        </template>
      </div>

    </div>
  </div>
`;

/* ── JSON syntax highlighting ──────────────────────────────────────── */

function highlight(json) {
  const tokenRe = /("(?:[^"\\]|\\.)*")(\s*:)?|true|false|null|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|[{}[\],]/g;
  let out  = "";
  let last = 0;

  for (const m of json.matchAll(tokenRe)) {
    out += esc(json.slice(last, m.index));
    last = m.index + m[0].length;

    const [full, str, colon] = m;

    if (str !== undefined) {
      out += colon !== undefined
        ? `<span class="sh-key">${esc(str)}</span>${esc(colon)}`
        : `<span class="sh-str">${esc(str)}</span>`;
    } else if (full === "true" || full === "false" || full === "null") {
      out += `<span class="sh-bool">${full}</span>`;
    } else if (/^-?\d/.test(full)) {
      out += `<span class="sh-num">${full}</span>`;
    } else {
      out += esc(full);
    }
  }

  return out + esc(json.slice(last));
}

/* ── DOM extraction helpers ────────────────────────────────────────── */

function parsePathParams(path) {
  const params = [];
  for (const m of path.matchAll(/\{([^}]+)\}/g)) params.push({ name: m[1] });
  return params;
}

/* ── Utilities ─────────────────────────────────────────────────────── */

function esc(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
