/**
 * @module import-path
 * @description Injects a "copy import path" button into autodoc signatures
 * so API readers can copy a fully-qualified symbol path (e.g.
 * ``mypkg.submod.Class.method``) with one click, instead of the URL anchor
 * that ``headerLinks`` already offers.
 *
 * Mounts on page load. Each ``dt.sig`` that carries an ``id`` attribute
 * matching a dotted module path gets a button inserted after its inline
 * ``.headerlink`` anchor. The button copies the id and flashes "Copied!"
 * for ~1.5s before reverting.
 */

const ICON_COPY =
  '<svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>' +
  '<path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>' +
  "</svg>";

const ICON_CHECK =
  '<svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<polyline points="20 6 9 17 4 12"/>' +
  "</svg>";

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

function makeButton(path) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "lumina-import-path";
  btn.setAttribute("aria-label", `Copy import path ${path}`);
  btn.setAttribute("title", `Copy ${path}`);
  btn.innerHTML = ICON_COPY + "<span>Copy path</span>";
  btn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    copyText(path).then(() => {
      btn.innerHTML = ICON_CHECK + "<span>Copied</span>";
      btn.classList.add("is-copied");
      setTimeout(() => {
        btn.innerHTML = ICON_COPY + "<span>Copy path</span>";
        btn.classList.remove("is-copied");
      }, 1500);
    });
  });
  return btn;
}

export default function bootImportPath() {
  const dts = document.querySelectorAll("dl.py > dt.sig[id]");
  dts.forEach((dt) => {
    const id = dt.getAttribute("id");
    // Only attach when the id looks like a dotted symbol path.
    if (!id || !id.includes(".")) return;
    // Don't duplicate if script somehow runs twice.
    if (dt.querySelector(".lumina-import-path")) return;
    const btn = makeButton(id);
    const headerlink = dt.querySelector("a.headerlink");
    if (headerlink) {
      headerlink.insertAdjacentElement("afterend", btn);
    } else {
      dt.appendChild(btn);
    }
  });
}
