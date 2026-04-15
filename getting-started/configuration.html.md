# Configuration

Everything you can configure in Lumina — theme options, accent colors, and a complete reference.

## Recommended Configuration

Most projects benefit from a few extensions and settings beyond the defaults. Here’s a practical starting point:

```python
extensions = [
    "myst_parser",           # Write docs in Markdown
    "sphinx_design",         # Cards, grids, tabs, badges
    "sphinx_copybutton",     # Copy button on code blocks
]

html_theme = "lumina"
html_theme_options = {
    "accent_color": "#10b981",                                          # Emerald (default)
    "source_repository": "https://github.com/you/your-project",        # Enables "Edit on GitHub"
    "source_branch": "main",
    "source_directory": "docs/",
}
```

## Theme Options Reference

All options go in `html_theme_options` in your `conf.py`. Every option has a sensible default, so you only need to set what you want to change.

### Appearance

| Option              | Type   | Default     | Description                                                                                                                                                                                                                                                                            |
|---------------------|--------|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `accent_color`      | string | `"#10b981"` | Primary brand color used for links, active states, and accents. Any valid CSS color.                                                                                                                                                                                                   |
| `dark_mode_default` | string | `"auto"`    | Initial color mode. `"auto"` follows system preference, `"light"` and `"dark"` force a mode.                                                                                                                                                                                           |
| `wide_layout`       | string | `"false"`   | Controls wide content layout (`60rem` instead of `48rem`). `"toggle"` shows a button in the header that lets readers switch (visible on viewports ≥1280px, persisted in browser). `"always"` forces wide mode permanently with no toggle. See [Wide Layout](../guides/wide-layout.md). |
| `logo_only`         | string | `"false"`   | When `"true"`, hides the project name in the header and shows only the logo.                                                                                                                                                                                                           |
| `light_logo`        | string | `""`        | Logo image for light mode (path relative to `_static`). Falls back to `html_logo`.                                                                                                                                                                                                     |
| `dark_logo`         | string | `""`        | Logo image for dark mode (path relative to `_static`). When set alone, displays in both modes. Set both `light_logo` and `dark_logo` for automatic switching.                                                                                                                          |
| `logo_icon`         | string | `""`        | Use a [Lucide icon](https://lucide.dev/icons/) as the site logo instead of an image. Pass the icon name (e.g. `"hexagon"`). Only used when no image logo is configured. See [Icons](../guides/icons.md).                                                                               |

### Announcement

| Option         | Type   | Default   | Description                                                                                                                                                                                                      |
|----------------|--------|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `announcement` | string | `""`      | HTML content for a dismissible banner above the header. Supports links and inline formatting. Users can dismiss it; the preference persists in `localStorage` and resets automatically when the content changes. |

### Navigation

| Option             | Type   | Default   | Description                                                                                                                                                                                              |
|--------------------|--------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `nav_links`        | list   | `[]`      | Links displayed in the header navigation bar. Each item needs `title` and `url` keys. Add `"external": True` for off-site links, or `"children"` with a list of `{title, url}` items for dropdown menus. |
| `nav_depth`        | string | `"3"`     | Maximum depth of the sidebar table of contents tree.                                                                                                                                                     |
| `show_toc`         | string | `"true"`  | Show or hide the right-side page table of contents.                                                                                                                                                      |
| `show_breadcrumbs` | string | `"true"`  | Show or hide the breadcrumb trail above the content.                                                                                                                                                     |
| `show_prev_next`   | string | `"true"`  | Show or hide previous/next page navigation at the bottom.                                                                                                                                                |
| `show_attribution` | string | `"true"`  | Show or hide the “Built with Lumina” attribution link in the sidebar footer.                                                                                                                             |
| `show_back_to_top` | string | `"true"`  | Show or hide the back-to-top button that appears when scrolling up.                                                                                                                                      |

### Version Switcher

| Option                   | Type   | Default   | Description                                                                                            |
|--------------------------|--------|-----------|--------------------------------------------------------------------------------------------------------|
| `version_switcher_json`  | string | `""`      | URL to a JSON file listing available documentation versions. Enables a version dropdown in the header. |
| `version_switcher_match` | string | `""`      | The current version string to highlight in the dropdown. Should match a `version` field in the JSON.   |

### Search

| Option           | Type   | Default      | Description                                                                                            |
|------------------|--------|--------------|--------------------------------------------------------------------------------------------------------|
| `search_backend` | string | `"pagefind"` | Search implementation. `"pagefind"` for Pagefind (recommended), `"sphinx"` for Sphinx built-in search. |

### HTTP API

These options control the interactive features on HTTP API endpoint pages. They require `sphinxcontrib-openapi` or `sphinxcontrib-httpdomain`. See [OpenAPI](../extensions/openapi.md) for setup.

| Option         | Type   | Default   | Description                                                                                                                                                                                                                                        |
|----------------|--------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `api_base_url` | string | `""`      | Default base URL for all HTTP API endpoints. Enables the “Copy as curl” button and “Try it out” panel. Individual blocks can override this with a `data-api-base-url` attribute on any ancestor element — see [OpenAPI](../extensions/openapi.md). |
| `try_it_out`   | string | `"true"`  | Set to `"false"` to hide the “Try it out” panel while keeping the “Copy as curl” button.                                                                                                                                                           |

### Source Links

These options enable the “Edit on GitHub” link in the table of contents sidebar.

| Option              | Type   | Default   | Description                                                                                      |
|---------------------|--------|-----------|--------------------------------------------------------------------------------------------------|
| `source_repository` | string | `""`      | URL to your source repository (e.g., `https://github.com/you/project`). Required for edit links. |
| `source_branch`     | string | `"main"`  | Branch name used in edit links.                                                                  |
| `source_directory`  | string | `"docs/"` | Path to the docs directory within your repository.                                               |
| `edit_uri`          | string | `"edit"`  | URI path component for edit links. Use `"edit"` for GitHub, `"blob"` for view-only links.        |

### Footer & Social

| Option         | Type   | Default   | Description                                                                                  |
|----------------|--------|-----------|----------------------------------------------------------------------------------------------|
| `social_links` | list   | `[]`      | Icon links in the header. Each item needs `icon` and `url` keys. Supported icon: `"github"`. |
| `footer_text`  | string | `""`      | Custom text displayed in the page footer.                                                    |

## Accent Colors

The `accent_color` option controls links, active navigation items, buttons, and other interactive elements. It applies to both light and dark modes automatically.

Here are some well-tested color choices:

| Color   | Hex       | Best for                                               |
|---------|-----------|--------------------------------------------------------|
| Emerald | `#10b981` | Default. Clean and professional.                       |
| Blue    | `#3b82f6` | Traditional documentation feel.                        |
| Violet  | `#8b5cf6` | Creative and modern projects.                          |
| Rose    | `#f43f5e` | Bold, attention-grabbing.                              |
| Amber   | `#f59e0b` | Warm, energetic. Ensure contrast on light backgrounds. |
| Teal    | `#14b8a6` | Calm, technical feel.                                  |

#### WARNING
Choose a color with sufficient contrast against both light and dark backgrounds. Avoid very light colors (pastels) — they become unreadable on white backgrounds.

## Full Configuration Example

Here’s a `conf.py` using every theme option:

```python
html_theme = "lumina"
html_theme_options = {
    # Appearance
    "accent_color": "#10b981",
    "dark_mode_default": "auto",
    "logo_only": "false",
    "light_logo": "logo-light.svg",
    "dark_logo": "logo-dark.svg",

    # Announcement
    "announcement": 'New in v2.0 — <a href="/changelog">see what changed</a>!',

    # Navigation
    "nav_links": [
        {"title": "Guide", "url": "getting-started"},
        {
            "title": "Reference",
            "children": [
                {"title": "Typography", "url": "reference/typography"},
                {"title": "Code Blocks", "url": "reference/code-blocks"},
            ],
        },
        {"title": "GitHub", "url": "https://github.com/you/project", "external": True},
    ],
    "nav_depth": "3",
    "show_toc": "true",
    "show_breadcrumbs": "true",
    "show_prev_next": "true",
    "show_attribution": "true",
    "show_back_to_top": "true",

    # Version switcher
    "version_switcher_json": "https://example.com/versions.json",
    "version_switcher_match": "1.17",

    # Search
    "search_backend": "pagefind",

    # HTTP API interactive features
    "api_base_url": "https://api.example.com/v1",
    "try_it_out": "true",

    # Source links (enables "Edit on GitHub")
    "source_repository": "https://github.com/you/project",
    "source_branch": "main",
    "source_directory": "docs/",
    "edit_uri": "edit",

    # Footer & social
    "social_links": [
        {"icon": "github", "url": "https://github.com/you/project"},
    ],
    "footer_text": "Built with Sphinx and Lumina.",
}
```

## Next Steps

Go deeper with CSS custom properties, custom fonts, syntax highlighting themes, and template overrides.
