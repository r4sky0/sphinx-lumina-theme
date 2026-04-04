# Lists & Tables

Structured content for organizing information.

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
   1. Install Python 3.10+
   2. Install Node.js 18+
2. Configure the project
   1. Copy the example config
   2. Update the settings
3. Run the build

## Task Lists

Track to-do items with checkboxes.

- <input class="task-list-item-checkbox" checked="checked" disabled="disabled" type="checkbox"> Set up project structure
- <input class="task-list-item-checkbox" checked="checked" disabled="disabled" type="checkbox"> Create base templates
- <input class="task-list-item-checkbox" disabled="disabled" type="checkbox"> Add search functionality
- <input class="task-list-item-checkbox" disabled="disabled" type="checkbox"> Write documentation
- <input class="task-list-item-checkbox" disabled="disabled" type="checkbox"> Publish to PyPI

The MyST syntax:

```markdown
- [x] Completed task
- [ ] Pending task
```

#### NOTE
Task lists require the `tasklist` MyST extension. See [Extensions](../extensions.md) for setup.

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
3. Finally, open the output in your browser.

## Tables

### When to Use Which Format

| Format          | Best for                                  | Limitations                                   |
|-----------------|-------------------------------------------|-----------------------------------------------|
| Markdown tables | Simple data with short cell content       | No multi-line cells, no spanning, no wrapping |
| List tables     | Complex content, long text, code in cells | More verbose syntax                           |

### Simple Markdown Tables

Basic Markdown tables with column alignment.

| Feature   | Status   | Notes                      |
|-----------|----------|----------------------------|
| Dark mode | Yes      | Light, dark, and auto      |
| Search    | Yes      | Pagefind + Sphinx fallback |
| Mobile    | Yes      | Responsive sidebar drawer  |
| i18n      | No       | Planned for v2             |

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

Tables with many columns scroll horizontally when they overflow the content area.

| Option              | Type   | Default    | Required   | Description           | Example   | Since   |
|---------------------|--------|------------|------------|-----------------------|-----------|---------|
| `accent_color`      | string | `#10b981`  | No         | Primary accent color  | `#3b82f6` | v0.1.0  |
| `dark_mode_default` | string | `auto`     | No         | Initial dark mode     | `dark`    | v0.1.0  |
| `show_toc`          | string | `true`     | No         | Show right-side TOC   | `false`   | v0.1.0  |
| `show_breadcrumbs`  | string | `true`     | No         | Show breadcrumb trail | `false`   | v0.1.0  |
| `show_prev_next`    | string | `true`     | No         | Show pagination       | `false`   | v0.1.0  |
| `nav_depth`         | string | `3`        | No         | Sidebar tree depth    | `2`       | v0.1.0  |
| `search_backend`    | string | `pagefind` | No         | Search provider       | `sphinx`  | v0.1.0  |

### List Tables

Use the `list-table` directive for complex tables that are hard to format in Markdown. List tables support multi-line cells, rich content, and precise column widths.

#### Theme Comparison

| Feature       | Lumina    | Furo     | PyData    | RTD      |
|---------------|-----------|----------|-----------|----------|
| Dark mode     | Auto      | Auto     | Auto      | No       |
| Search        | Pagefind  | Built-in | Built-in  | Built-in |
| CSS framework | Tailwind  | Custom   | Bootstrap | Custom   |
| JS framework  | Alpine.js | None     | None      | jQuery   |

The MyST syntax:

```markdown
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
```

### Tables with Rich Content

List tables can contain code, badges, and other inline elements.

| Option           | Status   | Usage                                |
|------------------|----------|--------------------------------------|
| `accent_color`   | stable   | Set with `"accent_color": "#hex"`    |
| `search_backend` | stable   | `"pagefind"` or `"sphinx"`           |
| `nav_links`      | stable   | JSON array of `{title, url}` objects |
