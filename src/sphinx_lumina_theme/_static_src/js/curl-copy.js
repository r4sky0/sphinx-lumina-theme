/**
 * Curl Copy
 *
 * Scans HTTP domain endpoints (dl.http) and injects a "Copy curl"
 * button into each signature card. Builds the curl command from
 * the rendered method, path, query parameters, headers, and JSON
 * body fields in the DOM.
 *
 * Called from boot() in app.js after Alpine.start().
 * The base URL is read from html_theme_options["api_base_url"],
 * output as a data attribute on <html> by the theme template.
 */

export default function curlCopy() {
  const baseUrl = document.documentElement.dataset.apiBaseUrl || "";
  const endpoints = document.querySelectorAll("dl.http");
  if (endpoints.length === 0) return;

  // Inject server URL badge once before the first endpoint on each page
  if (baseUrl) {
    injectServerBadge(endpoints[0], baseUrl);
  }

  endpoints.forEach((dl) => {
    injectButton(dl, baseUrl);
  });
}

function injectServerBadge(firstEndpoint, baseUrl) {
  const badge = document.createElement("div");
  badge.className = "lumina-api-server";

  const label = document.createElement("span");
  label.className = "lumina-api-server-label";
  label.textContent = "Server";

  const url = document.createElement("code");
  url.className = "lumina-api-server-url";
  url.textContent = baseUrl;

  badge.appendChild(label);
  badge.appendChild(url);
  firstEndpoint.parentNode.insertBefore(badge, firstEndpoint);
}

function injectButton(dl, baseUrl) {
  const sig = dl.querySelector("dt.sig");
  if (!sig) return;

  const btn = document.createElement("button");
  btn.className = "lumina-curl-copy";
  btn.setAttribute("aria-label", "Copy as curl");
  btn.title = "Copy as curl";
  setIcon(btn, "curl");

  btn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    const curl = buildCurl(dl, baseUrl);
    copyText(curl)
      .then(() => {
        btn.classList.add("is-copied");
        setIcon(btn, "check");
        setTimeout(() => {
          btn.classList.remove("is-copied");
          setIcon(btn, "curl");
        }, 1500);
      })
      .catch(() => {});
  });

  sig.appendChild(btn);
}

/* ── Icon rendering (safe DOM construction) ── */

function setIcon(btn, type) {
  // Clear existing children
  while (btn.firstChild) btn.removeChild(btn.firstChild);

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("width", "14");
  svg.setAttribute("height", "14");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("fill", "none");
  svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", "2");
  svg.setAttribute("stroke-linecap", "round");
  svg.setAttribute("stroke-linejoin", "round");

  if (type === "check") {
    const polyline = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "polyline"
    );
    polyline.setAttribute("points", "20 6 9 17 4 12");
    svg.appendChild(polyline);
  } else {
    const p1 = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "polyline"
    );
    p1.setAttribute("points", "16 18 22 12 16 6");
    const p2 = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "polyline"
    );
    p2.setAttribute("points", "8 6 2 12 8 18");
    svg.appendChild(p1);
    svg.appendChild(p2);
  }

  btn.appendChild(svg);
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

  // Build URL with query params
  let fullUrl = url;
  if (queryParams.length > 0) {
    const qs = queryParams.map((p) => `${p}=<value>`).join("&");
    fullUrl += `?${qs}`;
  }
  parts.push(`"${fullUrl}"`);

  // Add headers (skip Content-Type if we have a body — curl sets it with -d)
  for (const h of headers) {
    if (h.name.toLowerCase() === "content-type" && jsonFields.length > 0) {
      continue;
    }
    parts.push(`-H "${h.name}: ${h.value}"`);
  }

  // Add JSON body
  if (jsonFields.length > 0) {
    parts.push('-H "Content-Type: application/json"');
    const body = {};
    for (const f of jsonFields) {
      body[f.name] = placeholder(f.type);
    }
    parts.push(`-d '${JSON.stringify(body)}'`);
  }

  // Single-line for simple commands, multi-line for complex ones
  if (parts.length <= 2) {
    return parts.join(" ");
  }
  return parts.join(" \\\n  ");
}

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
  if (names.length >= 2) {
    return names[1].textContent.trim();
  }
  return "/";
}

function extractHeaders(dl) {
  return extractFieldSection(dl, "Request Headers");
}

function extractQueryParams(dl) {
  const items = extractFieldSection(dl, "Query Parameters");
  return items.map((i) => i.name);
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
  const dts = fieldList.querySelectorAll(":scope > dt");

  for (const dt of dts) {
    const dtText = dt.textContent.replace(/:$/, "").trim();
    if (!dtText.startsWith(label)) continue;

    const fieldDd = dt.nextElementSibling;
    if (!fieldDd || fieldDd.tagName.toLowerCase() !== "dd") continue;

    const lis = fieldDd.querySelectorAll("li");
    for (const li of lis) {
      const strong = li.querySelector("strong");
      const em = li.querySelector("em");
      if (strong) {
        const name = strong.textContent.trim();
        const type = em ? em.textContent.trim() : "string";
        let value = "";
        if (label === "Request Headers") {
          const text = li.textContent;
          const dashIdx = text.indexOf("\u2013");
          if (dashIdx !== -1) {
            value = text.substring(dashIdx + 1).trim().replace(/\.$/, "");
            const code = li.querySelector("code");
            if (code) value = code.textContent;
          }
        }
        items.push({ name, type, value });
      }
    }
  }

  return items;
}

function placeholder(type) {
  switch (type.toLowerCase()) {
    case "integer":
    case "int":
    case "number":
      return 0;
    case "boolean":
    case "bool":
      return true;
    case "array":
      return [];
    case "object":
      return {};
    default:
      return "";
  }
}

/* ── Clipboard ── */

function copyText(text) {
  if (navigator.clipboard) {
    return navigator.clipboard.writeText(text).catch(() => fallbackCopy(text));
  }
  return fallbackCopy(text);
}

function fallbackCopy(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.cssText = "position:fixed;opacity:0";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
  return Promise.resolve();
}
