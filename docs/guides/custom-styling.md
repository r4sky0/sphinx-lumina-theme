# Custom Styling

Override CSS custom properties, fonts, syntax highlighting themes, and templates for deeper customization.

## Migrating to Lumina 2

Lumina 2 refreshes the default design. Existing theme options still work, but custom CSS and template overrides need review.

- **Page actions:** Copy Markdown, edit links, and reading time now live in the page-actions menu. Overrides of `layout.html` or `components/toc.html` should use the new `components/page-actions.html` component.
- **Link colors:** `--lumina-accent` controls brand accents; `--lumina-link` controls readable text links and focus outlines. Set both for each mode if you customize tokens directly. The `accent_color` option derives both automatically.
- **Surfaces:** `--lumina-navigation-bg` and `--lumina-floating-bg` control the sidebar and floating menus separately from the page background.
- **Content:** Cards no longer lift or cast shadows; admonitions use a thin border on all sides. Heading sizes, weights, and spacing have changed.
- **Mobile navigation:** The page outline is now available below the breadcrumbs. `show_toc = "false"` hides both desktop and mobile outlines.

Rebuild your docs and check custom styles in both color modes, including mobile layouts. Use `html_short_title` for a shorter header label without changing your Sphinx project name.

## Adding a Custom Stylesheet

Create a CSS file and register it in your `conf.py`:

```{code-block} python
:caption: conf.py
html_static_path = ["_static"]
html_css_files = ["custom.css"]
```

Then create `docs/_static/custom.css` with your overrides.

## CSS Custom Properties

Lumina defines CSS custom properties for all visual tokens. Override them in your custom stylesheet. For a complete reference of every token, default value, and what each one controls, see {doc}`/reference/css-variables`.

### Core Colors

```{code-block} css
:caption: docs/_static/custom.css
/* Light mode overrides */
:root {
    --lumina-bg: #fdfdfc;              /* Main background */
    --lumina-bg-secondary: #f4f5f4;    /* Secondary surfaces */
    --lumina-text: #202624;            /* Primary text */
    --lumina-text-muted: #59635e;      /* Secondary text */
    --lumina-border: #dfe5e1;          /* Borders and dividers */
    --lumina-accent: #10b981;          /* Brand accents and active indicators */
    --lumina-accent-light: #eaf6ef;    /* Accent background tint */
    --lumina-link: #08764f;            /* Readable links and focus outlines */
    --lumina-navigation-bg: #f7f8f6;   /* Sidebar surface */
    --lumina-floating-bg: #fdfdfc;     /* Floating menus and search */
    --lumina-code-bg: #f6f7f6;         /* Inline code background */
}

/* Dark mode overrides */
[data-theme="dark"] {
    --lumina-bg: #151918;
    --lumina-bg-secondary: #202623;
    --lumina-text: #e9eeeb;
    --lumina-text-muted: #a8b5ac;
    --lumina-border: #303b34;
    --lumina-accent: #10b981;
    --lumina-accent-light: #1c3329;
    --lumina-link: #5ed9a3;
    --lumina-navigation-bg: #111613;
    --lumina-floating-bg: #242c27;
    --lumina-code-bg: #1b211e;
}
```

### Admonition Colors

Each admonition type has its own color property:

```css
/* Light mode */
:root {
    --lumina-adm-note: #2563eb;           /* Blue */
    --lumina-adm-tip: #08764f;            /* Green */
    --lumina-adm-warning: #f59e0b;        /* Amber */
    --lumina-adm-warning-text: #b45309;   /* Amber (darker, for text contrast) */
    --lumina-adm-danger: #dc2626;         /* Red */
    --lumina-adm-important: #7c3aed;      /* Purple */
    --lumina-adm-seealso: #0e7490;        /* Cyan */
}

/* Dark mode */
[data-theme="dark"] {
    --lumina-adm-note: #60a5fa;
    --lumina-adm-tip: #34d399;
    --lumina-adm-warning: #fbbf24;
    --lumina-adm-warning-text: #f59e0b;
    --lumina-adm-danger: #f87171;
    --lumina-adm-important: #a78bfa;
    --lumina-adm-seealso: #22d3ee;
}
```

## Fonts

Lumina ships with self-hosted fonts — no external CDN requests:

- **Source Sans 3** (400, 500, 600, 700) — body text
- **JetBrains Mono** (400, 500) — code blocks and inline code

To use your own fonts, override the font-family declarations in your custom CSS:

```css
body {
    font-family: "Inter", system-ui, sans-serif;
}

code, pre, .highlight {
    font-family: "Fira Code", ui-monospace, monospace;
}
```

:::{note}
If you use custom fonts, add the font files to your `_static/` directory and include the appropriate `@font-face` declarations.
:::

## Syntax Highlighting

Lumina ships five syntax highlighting presets — curated light/dark pairs tested for contrast on the theme's code block backgrounds. Set the `code_style` theme option to switch:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "code_style": "nord",
}
```

```{list-table} Available presets
:header-rows: 1
:widths: 15 20 20 45

* - Preset
  - Light style
  - Dark style
  - Character
* - `"default"`
  - default
  - monokai
  - Neutral baseline — familiar Pygments defaults
* - `"nord"`
  - tango
  - nord
  - Cool, crisp, precise — arctic calm
* - `"one-dark"`
  - friendly
  - one-dark
  - Warm, modern — Atom's popular syntax theme
* - `"gruvbox"`
  - gruvbox-light
  - gruvbox-dark
  - Earthy, bold — retro groove with warm tones
* - `"material"`
  - lovelace
  - material
  - Refined, editorial — Google's Material palette
```

### Custom styles

For full control, set `pygments_style` and `pygments_dark_style` directly in `conf.py`. When either is set, the `code_style` preset is ignored.

```{code-block} python
:caption: conf.py
pygments_style = "friendly"
pygments_dark_style = "dracula"
```

:::{tip}
Preview all available Pygments styles at [pygments.org/styles](https://pygments.org/styles/).
:::

## Hiding Page Elements

Selectively hide UI elements globally or per-page.

### Globally

```{code-block} python
:caption: conf.py
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

Lumina's templates are designed for extension. To override a specific component, create a `_templates/` directory:

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
