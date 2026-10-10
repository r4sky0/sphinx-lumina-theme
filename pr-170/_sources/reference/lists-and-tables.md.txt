# Lists & Tables

Make steps easy to follow and reference data easy to compare.

## Unordered Lists

- First item
- Second item
- Third item with **bold** and `code`

Nested unordered lists:

- Fruits
  - Apples
  - Bananas
    - Cavendish
    - Plantain
  - Cherries
- Vegetables
  - Carrots
  - Peas

## Ordered Lists

1. First step
2. Second step
3. Third step

Nested ordered lists:

1. Install dependencies
   1. Install Python 3.12+
   2. Install Node.js 18+
2. Configure the project
   1. Copy the example config
   2. Update the settings
3. Run the build

## Task Lists

Track to-do items with checkboxes.

- [x] Set up project structure
- [x] Create base templates
- [ ] Add search functionality
- [ ] Write documentation
- [ ] Publish to PyPI

The MyST syntax:

```markdown
- [x] Completed task
- [ ] Pending task
```

:::{note}
Task lists require the `tasklist` MyST extension. See {doc}`/extensions/myst-parser` for setup.
:::

## Rich Content in Lists

List items can contain paragraphs, code blocks, and other block elements.

1. First, configure the theme:

   ```python
   html_theme = "lumina"
   ```

2. Then build your documentation:

   ```bash
   uv run sphinx-build docs docs/_build/html
   ```

   :::{tip}
   Add `-W` to treat warnings as errors during CI builds.
   :::

3. Finally, open the output in your browser.

## Tables

### When to Use Which Format

```{list-table}
:header-rows: 1
:widths: 20 40 40

* - Format
  - Best for
  - Limitations
* - Markdown tables
  - Simple data with short cell content
  - No block content or spanning cells
* - List tables
  - Complex content, long text, code in cells
  - More verbose syntax
```

### Simple Markdown Tables

Basic Markdown tables with column alignment.

| Feature | Status | Notes |
|:--------|:------:|------:|
| Dark mode | Yes | Light, dark, and auto |
| Search | Yes | Pagefind + Sphinx fallback |
| Mobile | Yes | Responsive sidebar drawer |
| Reading time | Yes | Optional per-page estimate |

The MyST syntax:

```markdown
| Left aligned | Centered | Right aligned |
|:-------------|:--------:|--------------:|
| data         | data     |          data |
```

Alignment markers:
- `:---` left-align (default)
- `:---:` center
- `---:` right-align

### Wide Tables

Tables with many columns scroll horizontally on larger screens when they overflow the content area. On narrow screens, simple data tables become labelled rows so each record can be read without side-to-side scrolling; complex tables keep the horizontal-scroll fallback. The values below are illustrative.

| Option | Type | Default | Required | Description | Example | Since |
|--------|------|---------|----------|-------------|---------|-------|
| `accent_color` | string | `#10b981` | No | Primary accent color | `#3b82f6` | v1.0.0 |
| `dark_mode_default` | string | `auto` | No | Initial dark mode | `dark` | v1.0.0 |
| `show_toc` | string | `true` | No | Show right-side TOC | `false` | v1.0.0 |
| `show_breadcrumbs` | string | `true` | No | Show breadcrumb trail | `false` | v1.0.0 |
| `show_prev_next` | string | `true` | No | Show pagination | `false` | v1.0.0 |
| `nav_depth` | string | `4` | No | Sidebar tree depth | `2` | v1.0.0 |
| `search_backend` | string | `pagefind` | No | Search provider | `sphinx` | v1.0.0 |

### Interactive Tables

Add `:class: lumina-table-interactive` to an individual `list-table` or `csv-table`
directive to enable filtering and sorting. Try filtering by **guide**, or select
**Pages** to sort the example below. Select the same heading again to reverse the
order; **Reset** restores all rows in their original order.

```{list-table} Documentation inventory
:header-rows: 1
:class: lumina-table-interactive

* - Section
  - Format
  - Pages
* - Getting started
  - Guide
  - 4
* - Reference
  - Reference
  - 24
* - Extensions
  - Guide
  - 12
* - Contributing
  - Guide
  - 8
* - API
  - Reference
  - 36
```

The MyST syntax:

~~~markdown
```{list-table} Documentation inventory
:header-rows: 1
:class: lumina-table-interactive

* - Section
  - Pages
* - Getting started
  - 4
* - Reference
  - 24
```
~~~

For a Markdown pipe table, wrap it in a `table` directive:

~~~markdown
```{table} Documentation inventory
:class: lumina-table-interactive

| Section | Pages |
|---------|------:|
| Getting started | 4 |
| Reference | 24 |
```
~~~

Filtering matches text across all columns, ignoring case. Plain numbers, including
negative values and decimals, sort numerically; other values use natural text
order. Dates, currencies, and units are treated as text. Each table keeps its own
filter and sort state until the page is reloaded.

Interactive tables need one header row, one body, and a consistent number of
columns, without merged cells, nested tables, footer rows, or controls in the
headers. Unsupported tables stay static. Without JavaScript, all rows remain
readable. On narrow screens, interactive tables scroll horizontally so sortable
headings stay available. Printing includes all rows, even when a filter is active.

### List Tables

Use the `list-table` directive for complex tables that are hard to format in Markdown. List tables support multi-line cells, rich content, and precise column widths.

```{list-table} Theme Comparison
:header-rows: 1
:widths: 20 20 20 20 20

* - Feature
  - Lumina
  - Furo
  - PyData
  - RTD
* - Dark mode
  - Auto
  - Auto
  - Auto
  - No
* - Search
  - Pagefind
  - Built-in
  - Built-in
  - Built-in
* - CSS framework
  - Tailwind
  - Custom
  - Bootstrap
  - Custom
* - JS framework
  - Alpine.js
  - None
  - None
  - jQuery
```

The MyST syntax:

~~~markdown
```{list-table} Caption
:header-rows: 1
:widths: 20 20 20 20

* - Header 1
  - Header 2
  - Header 3
  - Header 4
* - Cell
  - Cell
  - Cell
  - Cell
```
~~~

### Tables with Rich Content

List tables can contain code, badges, and other inline elements.

```{list-table}
:header-rows: 1
:widths: 25 25 50

* - Option
  - Status
  - Usage
* - `accent_color`
  - {bdg-success}`stable`
  - Set with `"accent_color": "#hex"`
* - `search_backend`
  - {bdg-success}`stable`
  - `"pagefind"` or `"sphinx"`
* - `nav_links`
  - {bdg-success}`stable`
  - JSON array of `{title, url}` objects
```

:::{tip}
Use `:widths:` to control column proportions. Values are relative — `20 20 60` gives the third column three times the width of each first two.
:::
