/**
 * @module member-filter
 * @description Renders a small filter input above dense autodoc classes
 * so readers can hop to a specific method/attribute by name instead of
 * scrolling a 40-entry list.
 *
 * Activates only when a top-level ``dl.py.class`` contains more than
 * ``THRESHOLD`` nested member ``dl.py.method|attribute|property`` entries,
 * and only when the ``api_member_filter`` theme option is ``"true"``.
 * The theme option is surfaced on ``<html>`` via the ``data-api-member-filter``
 * attribute set in layout.html.
 */

const THRESHOLD = 8;

const ICON_SEARCH =
  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
  'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>';

function symbolName(dl) {
  const descname = dl.querySelector(":scope > dt.sig .sig-name.descname");
  if (descname && descname.textContent) return descname.textContent.trim();
  const id = dl.querySelector(":scope > dt.sig[id]")?.getAttribute("id") || "";
  const parts = id.split(".");
  return parts[parts.length - 1] || "";
}

function installFilter(classDl, members) {
  if (classDl.querySelector(":scope > dd > .lumina-member-filter")) return;

  const wrapper = document.createElement("div");
  wrapper.className = "lumina-member-filter";
  wrapper.setAttribute("role", "search");
  wrapper.innerHTML =
    ICON_SEARCH +
    '<input type="search" placeholder="Filter members..." ' +
    'aria-label="Filter class members" autocomplete="off">' +
    '<span class="lumina-member-filter-count" aria-live="polite"></span>';

  const input = wrapper.querySelector("input");
  const count = wrapper.querySelector(".lumina-member-filter-count");
  const total = members.length;
  count.textContent = `${total} of ${total}`;

  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    let visible = 0;
    members.forEach(({ dl, name }) => {
      const match = !q || name.toLowerCase().includes(q);
      dl.toggleAttribute("hidden", !match);
      if (match) visible += 1;
    });
    count.textContent = q ? `${visible} of ${total}` : `${total} of ${total}`;
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      input.value = "";
      input.dispatchEvent(new Event("input"));
      input.blur();
    }
  });

  const dd = classDl.querySelector(":scope > dd");
  if (!dd) return;
  dd.insertBefore(wrapper, dd.firstChild);
}

export default function bootMemberFilter() {
  if (document.documentElement.dataset.apiMemberFilter !== "true") return;

  document.querySelectorAll("dl.py.class").forEach((classDl) => {
    const memberSelector =
      ":scope > dd > dl.py.method, " +
      ":scope > dd > dl.py.classmethod, " +
      ":scope > dd > dl.py.staticmethod, " +
      ":scope > dd > dl.py.attribute, " +
      ":scope > dd > dl.py.property";
    const dls = Array.from(classDl.querySelectorAll(memberSelector));
    if (dls.length <= THRESHOLD) return;
    const members = dls.map((dl) => ({ dl, name: symbolName(dl) }));
    installFilter(classDl, members);
  });
}
