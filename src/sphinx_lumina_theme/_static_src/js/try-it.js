/**
 * @module try-it
 * @description Injects an interactive "Try It Out" request panel into each
 * HTTP-domain endpoint (``dl.http``). Extracts parameters from the rendered
 * DOM and sends real ``fetch`` requests. Credentials are shared in memory
 * only between endpoints using the same API base URL.
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
  extractBody,
  requestToCurl,
} from "./_http-api-utils.js";

import { copyText } from "./utils/clipboard.js";

// Credentials live only on this page and are isolated by the complete API base URL.
const credentials = new Map();
const emptyAuth = () => ({ type: "none", token: "", username: "", password: "", keyName: "", keyValue: "", keyIn: "header" });
function authFor(baseUrl) {
  let key;
  try { key = new URL(baseUrl, document.baseURI).href.replace(/\/$/, ""); }
  catch { key = baseUrl; }
  if (!credentials.has(key)) credentials.set(key, emptyAuth());
  return credentials.get(key);
}

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
    open: false,
    sending: false,
    response: null,
    showBearer: false,
    copiedResponse: false,
    copiedCurl: false,
    requestError: "",
    copyError: "",
    controller: null,
    auth: emptyAuth(),
    pathValues: {},
    queryValues: {},
    headerValues: {},
    customHeaders: [],
    bodyJson: "",
    contentType: "application/json",
    bodyError: null,
    method: "GET",
    path: "/",
    baseUrl: "",
    pathParams: [],
    queryParams: [],
    allHeaders: [],
    hasBody: false,
    extraHeaders: [],

    init() {
      const cfg = _configs.get(this.$el);
      if (!cfg) return;
      Object.assign(this, cfg);
      this.auth = authFor(this.baseUrl);
      this.$watch("baseUrl", () => { this.auth = authFor(this.baseUrl); });
      this.extraHeaders = this.allHeaders.filter(
        (h) => !["authorization", "content-type"].includes(h.name.toLowerCase()),
      );
      this.headerValues = Object.fromEntries(this.extraHeaders.map((h) => [h.name, h.value]));
    },

    get computedUrl() {
      const resolved = this.path.replace(/\{([^}]+)\}/g, (match, name) => {
        const value = String(this.pathValues[name] ?? "").trim();
        return value ? encodeURIComponent(value) : match;
      });
      const query = new URLSearchParams();
      for (const p of this.queryParams) {
        const value = String(this.queryValues[p.name] ?? "");
        if (value.trim()) query.append(p.name, value);
      }
      if (this.auth.type === "apiKey" && this.auth.keyIn === "query" && this.auth.keyName && this.auth.keyValue) {
        query.set(this.auth.keyName, this.auth.keyValue);
      }
      const base = this.baseUrl.trim().replace(/\/$/, "");
      return base + resolved + (query.size ? (resolved.includes("?") ? "&" : "?") + query : "");
    },

    get request() {
      const headers = {};
      for (const h of this.extraHeaders) {
        const value = (this.headerValues[h.name] || "").trim();
        if (value) headers[h.name.toLowerCase()] = value;
      }
      for (const h of this.customHeaders) {
        if (h.name.trim()) headers[h.name.trim().toLowerCase()] = h.value;
      }
      if (this.auth.type === "bearer" && this.auth.token.trim()) {
        headers.authorization = `Bearer ${this.auth.token.trim()}`;
      } else if (this.auth.type === "basic") {
        const bytes = new TextEncoder().encode(`${this.auth.username}:${this.auth.password}`);
        headers.authorization = "Basic " + btoa(Array.from(bytes, (b) => String.fromCharCode(b)).join(""));
      } else if (this.auth.type === "apiKey" && this.auth.keyIn === "header" && this.auth.keyName.trim()) {
        headers[this.auth.keyName.trim().toLowerCase()] = this.auth.keyValue;
      }
      const request = { method: this.method, url: this.computedUrl, headers };
      if (this.hasBody && this.bodyJson.trim()) {
        request.body = this.bodyJson;
        headers["content-type"] = this.contentType.trim();
      }
      return request;
    },

    get curlCommand() { return requestToCurl(this.request); },

    get formattedBody() {
      if (!this.response) return "";
      return this.response.isJson ? this.response.bodyHtml : esc(this.response.bodyText);
    },

    forgetAuth() { Object.assign(this.auth, emptyAuth()); },

    async send() {
      if (this.sending) return;
      this.requestError = "";
      this.bodyError = null;
      const missing = [...this.pathParams, ...this.queryParams.filter((p) => p.required)]
        .filter((p) => !String((this.pathParams.includes(p) ? this.pathValues : this.queryValues)[p.name] ?? "").trim());
      if (missing.length) {
        this.requestError = `Enter required parameters: ${missing.map((p) => p.name).join(", ")}.`;
        return;
      }
      if (this.hasBody && this.bodyJson.trim() && /(?:^|[/+])json(?:;|$)/i.test(this.contentType)) {
        try { JSON.parse(this.bodyJson); }
        catch {
          this.bodyError = "Request body is not valid JSON. Fix it before sending.";
          this.$refs.body.focus();
          return;
        }
      }
      let request;
      try {
        const base = new URL(this.baseUrl.trim(), document.baseURI);
        if (!this.baseUrl.trim() || !["http:", "https:"].includes(base.protocol) || base.username || base.password || base.search || base.hash) {
          throw new Error("Enter an HTTP(S) server URL without credentials, a query, or a fragment.");
        }
        if (this.auth.type === "apiKey" && (!this.auth.keyName.trim() || !this.auth.keyValue)) {
          throw new Error("Enter the API key name and value, or select No authentication.");
        }
        request = this.request;
        new Headers(request.headers); // Validate header names and values before fetching.
      } catch (err) {
        this.requestError = err.message;
        return;
      }
      this.sending = true;
      this.response = null;
      this.copiedResponse = false;
      this.controller = new AbortController();
      const timeout = setTimeout(() => this.controller?.abort(new DOMException("Request timed out after 30 seconds.", "TimeoutError")), 30000);
      const t0 = performance.now();
      try {
        const res = await fetch(request.url, {
          method: request.method, headers: request.headers, body: request.body,
          credentials: "omit", redirect: "error", signal: this.controller.signal,
        });
        let raw = await res.text();
        let isJson = false;
        if (raw && /json/i.test(res.headers.get("content-type") || "")) {
          try { raw = JSON.stringify(JSON.parse(raw), null, 2); isJson = true; }
          catch { /* Keep malformed JSON visible for debugging. */ }
        }
        this.response = {
          status: res.status,
          statusText: res.statusText,
          statusClass: res.status >= 500 ? "error" : res.status >= 400 ? "warning" : res.status >= 300 ? "info" : "success",
          elapsed: Math.round(performance.now() - t0),
          bodyText: raw || "(No response body)",
          bodyHtml: isJson ? highlight(raw) : null,
          headers: [...res.headers].map(([name, value]) => `${name}: ${value}`).join("\n"),
          url: res.url || request.url,
          isJson,
          error: false,
        };
      } catch (err) {
        this.response = {
          status: null,
          statusText: err.name === "AbortError" ? "Cancelled" : "Error",
          statusClass: "error",
          elapsed: Math.round(performance.now() - t0),
          bodyText: err.name === "AbortError" ? "Stopped waiting for this request. The server may still process it."
            : err.name === "TypeError" ? "Could not reach the API. Check the server URL, network, HTTPS and CORS settings. Redirects are not followed. Try Copy as curl to debug outside the browser."
            : err.message,
          headers: "", url: request.url, isJson: false, error: true,
        };
      } finally {
        clearTimeout(timeout);
        this.sending = false;
        this.controller = null;
      }
    },

    cancel() { this.controller?.abort(); },
    destroy() { this.cancel(); },

    async copyCurl() {
      this.copyError = "";
      try { await copyText(this.curlCommand); }
      catch { this.copyError = "Could not copy. Select the curl command below and copy it manually."; return; }
      this.copiedCurl = true;
      setTimeout(() => { this.copiedCurl = false; }, 1500);
    },

    async copyResponse() {
      this.copyError = "";
      try { await copyText(this.response.bodyText); }
      catch { this.copyError = "Could not copy. Select the response text and copy it manually."; return; }
      this.copiedResponse = true;
      setTimeout(() => { this.copiedResponse = false; }, 1500);
    },

    clear() {
      this.response = null;
      this.bodyError = null;
      this.requestError = "";
      this.copyError = "";
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
  if (!dd || dd.querySelector(":scope > .lumina-try-it")) return;

  const method      = extractMethod(dl);
  const path        = extractPath(dl);
  const pathParams  = parsePathParams(path);
  const queryParams = extractFieldSection(dd, "Query Parameters");
  const allHeaders  = extractFieldSection(dd, "Request Headers");
  const example = extractBody(dd);
  const hasBody = !["GET", "HEAD", "OPTIONS"].includes(method);

  /* Wrapper is the Alpine component root */
  const wrap = document.createElement("div");
  wrap.className = "lumina-try-it";
  wrap.setAttribute("x-data", "tryItPanel");

  /* Store config for Alpine init() to read via this.$el */
  _configs.set(wrap, { method, path, baseUrl, pathParams, queryParams, allHeaders, hasBody, bodyJson: example.body, contentType: example.contentType });
  wrap.setAttribute("x-id", "['api-field']");

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
          :aria-expanded="open.toString()"
          :aria-controls="$id('api-field', 'panel')">
    <svg class="lumina-try-it-chevron" width="10" height="10" viewBox="0 0 24 24"
         fill="none" stroke="currentColor" stroke-width="2.5"
         stroke-linecap="round" stroke-linejoin="round"
         :class="{ 'is-open': open }" aria-hidden="true">
      <polyline points="9 18 15 12 9 6"/>
    </svg>
    Try it out
  </button>

  <div class="lumina-try-it-grid" :class="{ 'is-open': open }" :inert="!open"
       :id="$id('api-field', 'panel')" :aria-hidden="!open">
    <div class="lumina-try-it-panel" @keydown.ctrl.enter.prevent="send()" @keydown.meta.enter.prevent="send()">

      <div class="lumina-try-it-param-row">
        <label class="lumina-try-it-param-name" :for="$id('api-field', 'server')">Server URL</label>
        <input class="lumina-try-it-input" :id="$id('api-field', 'server')" x-model="baseUrl"
               type="text" autocomplete="off" spellcheck="false" />
      </div>
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
            <label class="lumina-try-it-param-name" :for="$id('api-field', 'path-' + p.name)">
              <span x-text="p.name"></span>
              <span class="lumina-try-it-required" aria-label="required">*</span>
            </label>
            <input class="lumina-try-it-input"
                   :id="$id('api-field', 'path-' + p.name)"
                   x-model="pathValues[p.name]"
                   :placeholder="p.name" required aria-required="true"
                   type="text" autocomplete="off" spellcheck="false" />
          </div>
        </template>
      </div>

      <div class="lumina-try-it-section" x-show="queryParams.length">
        <div class="lumina-try-it-section-label">Query Parameters</div>
        <template x-for="p in queryParams" :key="p.name">
          <div class="lumina-try-it-param-row">
            <label class="lumina-try-it-param-name" :for="$id('api-field', 'query-' + p.name)">
              <span x-text="p.name"></span>
              <span class="lumina-try-it-type-tag" x-text="p.type" x-show="p.type"></span>
              <span class="lumina-try-it-required" x-show="p.required" aria-label="required">*</span>
            </label>
            <input class="lumina-try-it-input"
                   :id="$id('api-field', 'query-' + p.name)"
                   x-model="queryValues[p.name]"
                   :placeholder="p.required ? 'required' : 'optional'" :aria-required="p.required"
                   type="text" autocomplete="off" spellcheck="false" />
          </div>
        </template>
      </div>

      <details class="lumina-try-it-section lumina-try-it-details">
        <summary>Authentication <span x-show="auth.type !== 'none'" x-text="auth.type === 'apiKey' ? '· API key' : '· ' + auth.type"></span></summary>
        <p class="lumina-try-it-hint">Shared for this server on this page. Cleared on reload. Copied curl commands include credentials.</p>
        <div class="lumina-try-it-param-row">
          <label class="lumina-try-it-param-name" :for="$id('api-field', 'auth-type')">Type</label>
          <select class="lumina-try-it-input" :id="$id('api-field', 'auth-type')" x-model="auth.type">
            <option value="none">No authentication</option>
            <option value="bearer">Bearer token</option>
            <option value="basic">Basic authentication</option>
            <option value="apiKey">API key</option>
          </select>
        </div>
        <div class="lumina-try-it-param-row" x-show="auth.type === 'bearer'">
          <label class="lumina-try-it-param-name" :for="$id('api-field', 'token')">Bearer token</label>
          <input class="lumina-try-it-input" :id="$id('api-field', 'token')" x-model="auth.token"
                 :type="showBearer ? 'text' : 'password'" autocomplete="off" spellcheck="false" />
        </div>
        <div x-show="auth.type === 'basic'">
          <div class="lumina-try-it-param-row">
            <label class="lumina-try-it-param-name" :for="$id('api-field', 'username')">Username</label>
            <input class="lumina-try-it-input" :id="$id('api-field', 'username')" x-model="auth.username" autocomplete="off" />
          </div>
          <div class="lumina-try-it-param-row">
            <label class="lumina-try-it-param-name" :for="$id('api-field', 'password')">Password</label>
            <input class="lumina-try-it-input" :id="$id('api-field', 'password')" x-model="auth.password"
                   :type="showBearer ? 'text' : 'password'" autocomplete="off" />
          </div>
        </div>
        <div x-show="auth.type === 'apiKey'">
          <div class="lumina-try-it-param-row">
            <label class="lumina-try-it-param-name" :for="$id('api-field', 'key-name')">Key name</label>
            <input class="lumina-try-it-input" :id="$id('api-field', 'key-name')" x-model="auth.keyName" placeholder="X-API-Key" autocomplete="off" />
          </div>
          <div class="lumina-try-it-param-row">
            <label class="lumina-try-it-param-name" :for="$id('api-field', 'key-value')">Key value</label>
            <input class="lumina-try-it-input" :id="$id('api-field', 'key-value')" x-model="auth.keyValue"
                   :type="showBearer ? 'text' : 'password'" autocomplete="off" />
          </div>
          <div class="lumina-try-it-param-row">
            <label class="lumina-try-it-param-name" :for="$id('api-field', 'key-in')">Send in</label>
            <select class="lumina-try-it-input" :id="$id('api-field', 'key-in')" x-model="auth.keyIn">
              <option value="header">Header</option><option value="query">Query string</option>
            </select>
          </div>
        </div>
        <div class="lumina-try-it-actions" x-show="auth.type !== 'none'">
          <button type="button" class="lumina-try-it-clear" @click="showBearer = !showBearer"
                  :aria-pressed="showBearer" x-text="showBearer ? 'Hide credentials' : 'Show credentials'"></button>
          <button type="button" class="lumina-try-it-clear" @click="forgetAuth()">Clear credentials</button>
        </div>
      </details>

      <div class="lumina-try-it-section" x-show="extraHeaders.length">
        <div class="lumina-try-it-section-label">Headers</div>
        <template x-for="h in extraHeaders" :key="h.name">
          <div class="lumina-try-it-param-row">
            <label class="lumina-try-it-param-name" :for="$id('api-field', 'header-' + h.name)" x-text="h.name"></label>
            <input class="lumina-try-it-input"
                   :id="$id('api-field', 'header-' + h.name)"
                   x-model="headerValues[h.name]"
                   :placeholder="h.value || h.name"
                   type="text" autocomplete="off" spellcheck="false" />
          </div>
        </template>
      </div>

      <details class="lumina-try-it-section lumina-try-it-details">
        <summary>Additional headers</summary>
        <template x-for="(h, index) in customHeaders" :key="index">
          <div class="lumina-try-it-custom-header">
            <input class="lumina-try-it-input" x-model="h.name" aria-label="Header name" placeholder="Header name" />
            <input class="lumina-try-it-input" x-model="h.value" aria-label="Header value" placeholder="Value" />
            <button type="button" class="lumina-try-it-clear" @click="customHeaders.splice(index, 1)" aria-label="Remove header">Remove</button>
          </div>
        </template>
        <button type="button" class="lumina-try-it-clear" @click="customHeaders.push({name: '', value: ''})">Add header</button>
      </details>

      <div class="lumina-try-it-section" x-show="hasBody">
        <div class="lumina-try-it-param-row">
          <label class="lumina-try-it-param-name" :for="$id('api-field', 'content-type')">Content type</label>
          <input class="lumina-try-it-input" :id="$id('api-field', 'content-type')" x-model="contentType" />
        </div>
        <label class="lumina-try-it-section-label" :for="$id('api-field', 'body')">Request body</label>
        <textarea class="lumina-try-it-body"
                  x-model="bodyJson" x-ref="body" :id="$id('api-field', 'body')"
                  :aria-invalid="!!bodyError" :aria-describedby="$id('api-field', 'body-error')"
                  :class="{ 'has-error': bodyError }"
                  rows="5" spellcheck="false" autocomplete="off"
                  placeholder="Leave empty to send without a body"></textarea>
        <p class="lumina-try-it-body-error" :id="$id('api-field', 'body-error')" role="alert" x-show="bodyError" x-text="bodyError"></p>
      </div>

      <p class="lumina-try-it-body-error" role="alert" x-show="requestError" x-text="requestError"></p>
      <div class="lumina-try-it-actions">
        <button type="button" class="lumina-try-it-send"
                @click="send()" title="Send request (Ctrl/⌘ + Enter)"
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
        <button type="button" class="lumina-try-it-clear" @click="cancel()" x-show="sending">Cancel</button>
        <button type="button" class="lumina-try-it-clear" @click="copyCurl()" x-text="copiedCurl ? 'Copied!' : 'Copy as curl'"></button>
        <button type="button" class="lumina-try-it-clear"
                @click="clear()" x-show="response">Clear</button>
      </div>

      <p class="lumina-try-it-body-error" role="alert" x-show="copyError" x-text="copyError"></p>
      <details class="lumina-try-it-section lumina-try-it-details">
        <summary>Request command</summary>
        <pre class="lumina-try-it-res-body"><code x-text="curlCommand"></code></pre>
      </details>
      <p class="sr-only" role="status" x-text="sending ? 'Sending request' : response ? response.statusText : ''"></p>
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
            <p class="lumina-try-it-hint" x-text="response.url"></p>
            <details class="lumina-try-it-details" x-show="response.headers">
              <summary>Response headers</summary>
              <pre class="lumina-try-it-res-body"><code x-text="response.headers"></code></pre>
            </details>
            <pre class="lumina-try-it-res-body" tabindex="0" aria-label="Response body"
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
  return [...new Set([...path.matchAll(/\{([^}]+)\}/g)].map((m) => m[1]))].map((name) => ({ name }));
}

/* ── Utilities ─────────────────────────────────────────────────────── */

function esc(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
