# Customization

Everything you can configure in Lumina — theme options, colors, and CSS custom properties.

## Theme Options Reference

All options are set in `html_theme_options` in your `conf.py`. Every option has a sensible default, so you only need to set what you want to change.

### Appearance

```{list-table}
:header-rows: 1
:widths: 25 15 15 45

* - Option
  - Type
  - Default
  - Description
* - `accent_color`
  - string
  - `"#10b981"`
  - Primary brand color used for links, active states, and accents. Any valid CSS color.
* - `dark_mode_default`
  - string
  - `"auto"`
  - Initial color mode. `"auto"` follows system preference, `"light"` and `"dark"` force a mode.
* - `logo_only`
  - string
  - `"false"`
  - When `"true"`, hides the project name in the header and shows only the logo.
```

### Navigation

```{list-table}
:header-rows: 1
:widths: 25 15 15 45

* - Option
  - Type
  - Default
  - Description
* - `nav_links`
  - list
  - `[]`
  - Links displayed in the header navigation bar. Each item needs `title` and `url` keys. Add `"external": True` for off-site links.
* - `nav_depth`
  - string
  - `"3"`
  - Maximum depth of the sidebar table of contents tree.
* - `show_toc`
  - string
  - `"true"`
  - Show or hide the right-side page table of contents.
* - `show_breadcrumbs`
  - string
  - `"true"`
  - Show or hide the breadcrumb trail above the content.
* - `show_prev_next`
  - string
  - `"true"`
  - Show or hide previous/next page navigation at the bottom.
```

### Search

```{list-table}
:header-rows: 1
:widths: 25 15 15 45

* - Option
  - Type
  - Default
  - Description
* - `search_backend`
  - string
  - `"pagefind"`
  - Search implementation. `"pagefind"` for Pagefind (recommended), `"sphinx"` for Sphinx built-in search.
```

### Source Links

These options enable the "Edit on GitHub" link in the table of contents sidebar.

```{list-table}
:header-rows: 1
:widths: 25 15 15 45

* - Option
  - Type
  - Default
  - Description
* - `source_repository`
  - string
  - `""`
  - URL to your source repository (e.g., `https://github.com/you/project`). Required for edit links.
* - `source_branch`
  - string
  - `"main"`
  - Branch name used in edit links.
* - `source_directory`
  - string
  - `"docs/"`
  - Path to the docs directory within your repository.
* - `edit_uri`
  - string
  - `"edit"`
  - URI path component for edit links. Use `"edit"` for GitHub, `"blob"` for view-only links.
```

### Footer & Social

```{list-table}
:header-rows: 1
:widths: 25 15 15 45

* - Option
  - Type
  - Default
  - Description
* - `social_links`
  - list
  - `[]`
  - Icon links in the header. Each item needs `icon` and `url` keys. Supported icon: `"github"`.
* - `footer_text`
  - string
  - `""`
  - Custom text displayed in the page footer.
```

## Full Configuration Example

Here's a `conf.py` using every theme option:

```{code-block} python
:caption: conf.py — Complete theme configuration
html_theme = "lumina"
html_theme_options = {
    # Appearance
    "accent_color": "#10b981",
    "dark_mode_default": "auto",
    "logo_only": "false",

    # Navigation
    "nav_links": [
        {"title": "Guide", "url": "getting-started"},
        {"title": "Reference", "url": "reference/typography"},
        {"title": "GitHub", "url": "https://github.com/you/project", "external": True},
    ],
    "nav_depth": "3",
    "show_toc": "true",
    "show_breadcrumbs": "true",
    "show_prev_next": "true",

    # Search
    "search_backend": "pagefind",

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

## Accent Colors

The `accent_color` option controls links, active navigation items, buttons, and other interactive elements. It applies to both light and dark modes automatically.

Here are some well-tested color choices:

```{list-table}
:header-rows: 1
:widths: 20 20 60

* - Color
  - Hex
  - Best for
* - Emerald
  - `#10b981`
  - Default. Clean and professional.
* - Blue
  - `#3b82f6`
  - Traditional documentation feel.
* - Violet
  - `#8b5cf6`
  - Creative and modern projects.
* - Rose
  - `#f43f5e`
  - Bold, attention-grabbing.
* - Amber
  - `#f59e0b`
  - Warm, energetic. Ensure contrast on light backgrounds.
* - Teal
  - `#14b8a6`
  - Calm, technical feel.
```

:::{warning}
Choose a color with sufficient contrast against both light and dark backgrounds. Avoid very light colors (pastels) — they become unreadable on white backgrounds.
:::

## CSS Custom Properties

Lumina defines CSS custom properties that you can override for deeper customization. Add a custom stylesheet to your project:

```{code-block} python
:caption: conf.py
html_static_path = ["_static"]
html_css_files = ["custom.css"]
```

Then create `docs/_static/custom.css`:

### Core Colors

```{code-block} css
:caption: docs/_static/custom.css
/* Light mode overrides */
:root {
    --lumina-bg: #fcfcfc;              /* Main background */
    --lumina-bg-secondary: #f4f4f5;    /* Secondary background (sidebar, code blocks) */
    --lumina-text: #18181b;            /* Primary text */
    --lumina-text-muted: #52525b;      /* Secondary text */
    --lumina-border: #e4e4e7;          /* Borders and dividers */
    --lumina-accent: #10b981;          /* Links, active states */
    --lumina-accent-light: #ecfdf5;    /* Accent background tint */
    --lumina-code-bg: #f4f4f5;         /* Inline code background */
}

/* Dark mode overrides */
[data-theme="dark"] {
    --lumina-bg: #18181b;
    --lumina-bg-secondary: #27272a;
    --lumina-text: #fafafa;
    --lumina-text-muted: #a1a1aa;
    --lumina-border: #3f3f46;
    --lumina-accent: #34d399;
    --lumina-accent-light: #064e3b;
    --lumina-code-bg: #27272a;
}
```

### Admonition Colors

Each admonition type has its own color property:

```css
:root {
    --lumina-adm-note: #3b82f6;        /* Blue */
    --lumina-adm-tip: #10b981;         /* Green */
    --lumina-adm-warning: #f59e0b;     /* Amber */
    --lumina-adm-danger: #ef4444;      /* Red */
    --lumina-adm-important: #8b5cf6;   /* Purple */
    --lumina-adm-seealso: #14b8a6;     /* Teal */
}
```

## Fonts

Lumina ships with self-hosted fonts — no external CDN requests:

- **Source Sans 3** (400, 500, 600, 700) — body text
- **JetBrains Mono** (400, 500) — code blocks and inline code

To use your own fonts, override the font-family in your custom CSS:

```css
:root {
    --lumina-font-body: "Inter", system-ui, sans-serif;
    --lumina-font-code: "Fira Code", monospace;
}
```

:::{note}
If you use custom fonts, you are responsible for adding the font files to your `_static/` directory and including the appropriate `@font-face` declarations.
:::

## Syntax Highlighting

Lumina uses separate Pygments styles for light and dark modes:

- **Light mode**: `default` style
- **Dark mode**: `monokai` style

To change them, set the Pygments options in your `conf.py`:

```python
pygments_style = "friendly"           # Light mode
pygments_dark_style = "dracula"       # Dark mode (Lumina extension)
```

:::{tip}
Preview available Pygments styles at [pygments.org/styles](https://pygments.org/styles/).
:::

## Hiding Page Elements

You can selectively hide UI elements per-page using `html_theme_options` or on specific pages using file-level metadata.

### Globally

```python
html_theme_options = {
    "show_toc": "false",           # Hide right-side TOC on all pages
    "show_breadcrumbs": "false",   # Hide breadcrumbs on all pages
    "show_prev_next": "false",     # Hide prev/next navigation
}
```

### Per-page

Use MyST front matter to override the template:

```yaml
---
sd_hide_title: true    # Hide the page title (useful for landing pages)
---
```

## Custom Templates

Lumina's templates are designed for extension. To override a specific component, create a `_templates/` directory and add your own version:

```{code-block} python
:caption: conf.py
templates_path = ["_templates"]
```

Then create a template that extends the original:

```{code-block} html+jinja
:caption: docs/_templates/layout.html
{% extends "!layout.html" %}

{% block extrahead %}
{{ super() }}
<link rel="stylesheet" href="{{ pathto('_static/custom.css', 1) }}">
{% endblock %}
```

The `!` prefix tells Sphinx to use the theme's original template as the base, so you only override the blocks you need.
