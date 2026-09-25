/**
 * Wraps tables for scrolling and prepares mobile labels or opt-in controls
 * before Alpine starts. Complex tables keep the horizontal-scroll fallback.
 */
export default function responsiveTables() {
  document.querySelectorAll(".lumina-article table").forEach((table) => {
    if (table.parentElement.classList.contains("lumina-table-scroll")) return;
    const scroll = document.createElement("div");
    scroll.className = "lumina-table-scroll";
    scroll.tabIndex = 0;
    scroll.setAttribute("role", "region");
    scroll.setAttribute("aria-label", table.caption?.textContent.trim() || "Table");
    table.before(scroll);
    scroll.append(table);

    const headers = Array.from(table.tHead?.rows[0]?.cells || []);
    const labels = headers.map((header) => header.textContent.trim());
    const rows = Array.from(table.tBodies[0]?.rows || []);

    if (
      table.tHead?.rows.length !== 1 ||
      table.tBodies.length !== 1 ||
      table.querySelector("table") ||
      !labels.length ||
      labels.some((label) => !label) ||
      !rows.length ||
      headers.some((header) => header.colSpan !== 1 || header.rowSpan !== 1) ||
      rows.some(
        (row) =>
          row.children.length !== labels.length ||
          Array.from(row.children).some((cell) => cell.colSpan !== 1 || cell.rowSpan !== 1),
      )
    ) {
      return;
    }

    if (
      table.classList.contains("lumina-table-interactive") &&
      !table.tFoot &&
      !table.tHead.querySelector("a, button, input, select, textarea")
    ) {
      const panel = document.createElement("div");
      panel.className = "lumina-table-panel";
      panel.setAttribute("x-data", "tableControls");
      scroll.before(panel);
      panel.append(scroll);
      return;
    }

    rows.forEach((row) => {
      Array.from(row.children).forEach((cell, index) => {
        cell.dataset.label = labels[index];
      });
    });
    table.classList.add("lumina-table-stackable");
  });
}
