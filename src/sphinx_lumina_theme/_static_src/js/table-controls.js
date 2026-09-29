/** Per-table filtering and sorting, enabled by lumina-table-interactive. */
export default function tableControls() {
  let table, headers, rows;
  const collator = new Intl.Collator(document.documentElement.lang || undefined, {
    numeric: true, sensitivity: "base",
  });

  return {
    query: "",
    column: -1,
    descending: false,
    visible: 0,
    total: 0,

    init() {
      table = this.$el.querySelector("table");
      headers = Array.from(table.tHead.rows[0].cells);
      rows = Array.from(table.tBodies[0].rows).map((element) => ({
        element,
        values: Array.from(element.cells, (cell) => cell.textContent.trim()),
        text: element.textContent.toLocaleLowerCase(),
      }));
      this.total = this.visible = rows.length;
      this.$el.insertAdjacentHTML("afterbegin", `
        <div class="lumina-table-toolbar">
          <label>Filter rows
            <input type="search" x-model="query" placeholder="Type to filter…">
          </label>
          <span role="status" x-text="visible + ' of ' + total + ' rows'"></span>
          <button type="button" x-on:click="reset()"
                  x-bind:disabled="!query && column === -1">Reset</button>
        </div>
      `);
      this.$el.insertAdjacentHTML("beforeend", `
        <p class="lumina-table-empty" x-show="visible === 0" style="display: none">
          No matching rows. Try another term or reset the table.
        </p>
      `);
      headers.forEach((header, index) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "lumina-table-sort";
        button.setAttribute("x-on:click", `sort(${index})`);
        const content = header.children.length === 1 && header.firstElementChild.matches("p")
          ? header.firstElementChild : header;
        button.append(...content.childNodes);
        const indicator = document.createElement("span");
        indicator.setAttribute("aria-hidden", "true");
        indicator.setAttribute("x-text", `column === ${index} ? (descending ? '↓' : '↑') : '↕'`);
        button.append(indicator);
        content.append(button);
        header.setAttribute("scope", "col");
      });
      this.$watch("query", () => this.apply());
    },

    sort(column) {
      this.descending = this.column === column && !this.descending;
      this.column = column;
      this.apply();
    },

    reset() {
      this.query = "";
      this.column = -1;
      this.descending = false;
      this.apply();
    },

    apply() {
      const query = this.query.trim().toLocaleLowerCase();
      const ordered = [...rows];
      if (this.column !== -1) {
        const column = this.column;
        // ponytail: plain numbers and natural text only; add explicit types for dates/currency if needed.
        const numeric = rows.every(({ values }) => /^[+-]?(?:\d+\.?\d*|\.\d+)$/.test(values[column]));
        ordered.sort((a, b) => {
          const result = numeric
            ? Number(a.values[column]) - Number(b.values[column])
            : collator.compare(a.values[column], b.values[column]);
          return this.descending ? -result : result;
        });
      }
      this.visible = 0;
      ordered.forEach(({ element, text }) => {
        element.hidden = !text.includes(query);
        if (!element.hidden) this.visible++;
      });
      // Moving existing rows preserves links, markup, and Alpine state.
      window.Alpine.mutateDom(() => {
        table.tBodies[0].append(...ordered.map(({ element }) => element));
      });
      headers.forEach((header, index) => {
        if (index === this.column) {
          header.setAttribute("aria-sort", this.descending ? "descending" : "ascending");
        } else {
          header.removeAttribute("aria-sort");
        }
      });
    },
  };
}
