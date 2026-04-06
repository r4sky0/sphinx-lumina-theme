# Navigation

Configure header links, social icons, sidebar depth, and breadcrumbs.

## Header Navigation Links

Add links to your site header for quick access to key pages:

```python
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

```python
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

```python
html_theme_options = {
    "social_links": [
        {"icon": "github", "url": "https://github.com/you/your-project"},
    ],
}
```

## Sidebar Depth

Control how deep the sidebar table of contents tree expands:

```python
html_theme_options = {
    "nav_depth": "3",   # Default: 3 levels deep
}
```

## Breadcrumbs

The breadcrumb trail above the content helps readers orient themselves. To hide it:

```python
html_theme_options = {
    "show_breadcrumbs": "false",
}
```

## Page Table of Contents

The right-side page outline shows h2 and h3 headings. To hide it:

```python
html_theme_options = {
    "show_toc": "false",
}
```

## Previous / Next Navigation

Page-level previous/next links appear at the bottom of each page. To hide them:

```python
html_theme_options = {
    "show_prev_next": "false",
}
```

## Version Switcher

Display a dropdown in the header that lets readers switch between documentation versions. The version list loads from a JSON file you host alongside your docs.

### Setup

1. **Create a `versions.json` file** and host it at a stable URL:

```json
[
  {"version": "latest", "url": "https://example.com/en/latest/", "name": "dev (latest)"},
  {"version": "1.17", "url": "https://example.com/en/1.17/"},
  {"version": "1.16", "url": "https://example.com/en/1.16/"}
]
```

Each entry has:

- **`version`** (required) – version identifier, used to match `version_switcher_match`
- **`url`** (required) – base URL for that version’s docs (must end with `/`)
- **`name`** (optional) – display label, falls back to `version`

1. **Configure the theme** in your `conf.py`:

```python
html_theme_options = {
    "version_switcher_json": "https://example.com/versions.json",
    "version_switcher_match": "1.17",
}
```

The `version_switcher_match` value should match a `version` field in your JSON. The dropdown highlights that entry as “(current)”.

### How It Works

When a reader selects a different version, the switcher navigates to the same page path on the selected version’s URL. For example, viewing `https://example.com/en/1.17/guides/search.html` and selecting “latest” navigates to `https://example.com/en/latest/guides/search.html`.
