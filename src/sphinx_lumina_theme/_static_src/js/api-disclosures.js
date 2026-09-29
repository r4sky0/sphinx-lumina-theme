/**
 * @module api-disclosures
 * @description Collapses API definitions while preserving Sphinx signatures,
 * nested members, cross-references, and the fully readable no-JavaScript page.
 */
export default function apiDisclosures() {
  const definitions = [...document.querySelectorAll("dl.http, dl.py, dl.js")];
  const expanded = document.documentElement.dataset.apiExpanded === "true";
  const controls = [];

  for (const definition of definitions) {
    const signatures = [...definition.querySelectorAll(":scope > dt.sig")];
    const body = definition.querySelector(":scope > dd");
    if (!signatures.length || !body || definition.querySelector(":scope > dt > .lumina-api-toggle")) continue;
    body.id ||= `${signatures[0].id || 'api-' + controls.length}-details`;
    const buttons = signatures.map((sig) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "lumina-api-toggle";
      button.setAttribute("aria-label", `Details for ${sig.textContent.trim().split('¶')[0].trim()}`);
      button.setAttribute("aria-controls", body.id);
      sig.prepend(button);
      // Signature links and copy buttons retain their own actions.
      sig.addEventListener("click", (event) => {
        if (!event.target.closest("a, button") || event.target.closest(".lumina-api-toggle")) setOpen(body.hidden);
      });
      return button;
    });
    const setOpen = (open) => {
      body.hidden = !open;
      buttons.forEach((button) => button.setAttribute("aria-expanded", String(open)));
    };
    setOpen(expanded);
    controls.push({ definition, setOpen });
  }
  if (!controls.length) return;

  const toolbar = document.createElement("div");
  toolbar.className = "lumina-api-toolbar";
  toolbar.setAttribute("role", "group");
  toolbar.setAttribute("aria-label", "API display");
  for (const [label, open] of [["Expand all", true], ["Collapse all", false]]) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.addEventListener("click", () => controls.forEach((control) => control.setOpen(open)));
    toolbar.appendChild(button);
  }
  controls[0].definition.before(toolbar);

  const revealHash = () => {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    const parents = controls.filter(({ definition }) => definition.contains(target));
    if (!parents.length) return;
    parents.forEach((control) => control.setOpen(true));
    requestAnimationFrame(() => target.scrollIntoView({ block: "start", behavior: "instant" }));
  };
  window.addEventListener("hashchange", revealHash);
  revealHash();
}
