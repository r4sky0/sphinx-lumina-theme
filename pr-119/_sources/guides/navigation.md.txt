# Navigation

Configure header links, social icons, sidebar depth, and breadcrumbs.

## Header Navigation Links

Add links to your site header for quick access to key pages:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "nav_links": [
        {"title": "Guide", "url": "getting-started"},
        {"title": "API", "url": "api/index"},
        {"title": "GitHub", "url": "https://github.com/you/your-project", "external": True},
    ],
}
```

### Dropdown Menus

Create dropdown navigation menus with the `children` key:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "nav_links": [
        {
            "title": "Reference",
            "children": [
                {"title": "Typography", "url": "reference/typography"},
                {"title": "Code Blocks", "url": "reference/code-blocks"},
            ],
        },
    ],
}
```

## Social Links

Display icon links in the header (currently supports GitHub):

```{code-block} python
:caption: conf.py
html_theme_options = {
    "social_links": [
        {"icon": "github", "url": "https://github.com/you/your-project"},
    ],
}
```

## Sidebar Depth

Control how deep the sidebar table of contents tree expands:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "nav_depth": "4",   # Default: 4 levels deep
}
```

## Collapsible Sidebar Items

Every branch in the left sidebar can be collapsed or expanded via a chevron
toggle that appears next to its label. Behavior:

- The branch that contains the **current page** is auto-expanded on load,
  along with all of its ancestors. Readers always see where they are.
- Every other branch is expanded by default, but can be collapsed with a
  single click on its chevron.
- State is recomputed on each page load — it is not persisted across
  navigations.

### Marking a branch collapsed by default

If a branch should start **collapsed** (until a reader visits a page inside
it), add `nav_collapsed: true` to the frontmatter of its index page.

For MyST Markdown:

````{code-block} markdown
:caption: guides/advanced/index.md
---
nav_collapsed: true
---

# Advanced Topics
````

For reStructuredText, use a field list at the top of the document:

```rst
:nav_collapsed: true

Advanced Topics
===============
```

The branch auto-expands whenever the reader is viewing a page inside it,
so collapsed-by-default entries never hide the current page.

## Breadcrumbs

The breadcrumb trail above the content helps readers orient themselves. To hide it:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "show_breadcrumbs": "false",
}
```

## Page Table of Contents

The right-side page outline shows h2 and h3 headings. To hide it:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "show_toc": "false",
}
```

## Previous / Next Navigation

Page-level previous/next links appear at the bottom of each page. To hide them:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "show_prev_next": "false",
}
```

## Doc Sections

Group your documentation into distinct sections, each with its own icon, color, and sidebar navigation. A dropdown at the top of the sidebar lets readers switch between them — useful when your docs serve different audiences (e.g., users vs. developers) or cover separate products.

### Setup

Define your sections in `html_theme_options`:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "doc_sections": [
        {
            "name": "User Documentation",
            "description": "Installation, guides & reference",
            "icon": "book-open",
            "color": "#10b981",
            "default": True,
            "link": "getting-started/index",
        },
        {
            "path": "contributing",
            "name": "Developer Documentation",
            "description": "Architecture & development",
            "icon": "code",
            "color": "#8b5cf6",
        },
    ],
}
```

Each section has:
- **`name`** (required) -- display name in the switcher dropdown
- **`description`** (required) -- short tagline shown below the name
- **`icon`** (required) -- a [Lucide icon](https://lucide.dev/icons/) name (e.g., `"book-open"`, `"code"`)
- **`color`** (required) -- hex color for the icon badge and section name in the switcher
- **`path`** or **`paths`** -- directory prefixes that belong to this section. Use `path` for a single directory (e.g., `"contributing"`), or `paths` for multiple directories grouped under one section.
- **`default`** -- set to `True` on one section to make it the catch-all. Any page not claimed by another section's explicit paths automatically belongs to the default section.
- **`link`** -- page to navigate to when clicking this section in the dropdown (e.g., `"getting-started/index"`). Defaults to the first entry in `path`/`paths`.

### How It Works

When a reader visits a page that belongs to a section, the sidebar shows only that section's navigation tree. The dropdown at the top highlights the active section and lets readers jump to any other section's index page.

One section can be marked as `"default": True`. That section automatically includes every page not explicitly assigned to another section — you don't need to list every directory. This is the simplest way to split docs into two groups like "User Documentation" (everything) and "Developer Documentation" (just `contributing/`).

Section colors are contained to the switcher dropdown — they don't affect the rest of the page's accent color.

## Version Switcher

Display a dropdown in the header that lets readers switch between documentation versions. The version list loads from a JSON file you host alongside your docs.

### Setup

1. **Create a `versions.json` file** and host it at a stable URL:

```{code-block} json
:caption: versions.json
[
  {"version": "latest", "url": "https://example.com/en/latest/", "name": "dev (latest)"},
  {"version": "1.17", "url": "https://example.com/en/1.17/"},
  {"version": "1.16", "url": "https://example.com/en/1.16/"}
]
```

Each entry has:
- **`version`** (required) -- version identifier, used to match `version_switcher_match`
- **`url`** (required) -- base URL for that version's docs (must end with `/`)
- **`name`** (optional) -- display label, falls back to `version`

2. **Configure the theme** in your `conf.py`:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "version_switcher_json": "https://example.com/versions.json",
    "version_switcher_match": "1.17",
}
```

The `version_switcher_match` value should match a `version` field in your JSON. The dropdown highlights that entry as "(current)".

### How It Works

When a reader selects a different version, the switcher navigates to the same page path on the selected version's URL. For example, viewing `https://example.com/en/1.17/guides/search.html` and selecting "latest" navigates to `https://example.com/en/latest/guides/search.html`.
