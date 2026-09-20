/**
 * Adds column labels so simple data tables can become readable row cards on
 * narrow screens. Complex tables keep the horizontal-scroll fallback.
 */
export default function responsiveTables() {
  document.querySelectorAll(".lumina-article table").forEach((table) => {
    const headers = Array.from(table.querySelectorAll("thead th"));
    const labels = headers.map((header) => header.textContent.trim());
    const rows = Array.from(table.querySelectorAll("tbody tr"));

    if (
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

    rows.forEach((row) => {
      Array.from(row.children).forEach((cell, index) => {
        cell.dataset.label = labels[index];
      });
    });
    table.classList.add("lumina-table-stackable");
  });
}
