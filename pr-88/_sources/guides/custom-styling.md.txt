# Custom Styling

Override CSS custom properties, fonts, syntax highlighting themes, and templates for deeper customization.

## Adding a Custom Stylesheet

Create a CSS file and register it in your `conf.py`:

```{code-block} python
:caption: conf.py
html_static_path = ["_static"]
html_css_files = ["custom.css"]
```

Then create `docs/_static/custom.css` with your overrides.

## CSS Custom Properties

Lumina defines CSS custom properties for all visual tokens. Override them in your custom stylesheet.

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
    --lumina-bg: #09090b;
    --lumina-bg-secondary: #18181b;
    --lumina-text: #fafafa;
    --lumina-text-muted: #a1a1aa;
    --lumina-border: #27272a;
    --lumina-accent: #10b981;
    --lumina-accent-light: #022c22;
    --lumina-code-bg: #1c1c20;
}
```

### Admonition Colors

Each admonition type has its own color property:

```css
/* Light mode */
:root {
    --lumina-adm-note: #3b82f6;           /* Blue */
    --lumina-adm-tip: #10b981;            /* Green */
    --lumina-adm-warning: #f59e0b;        /* Amber */
    --lumina-adm-warning-text: #d97706;   /* Amber (darker, for text contrast) */
    --lumina-adm-danger: #ef4444;         /* Red */
    --lumina-adm-important: #8b5cf6;      /* Purple */
    --lumina-adm-seealso: #14b8a6;        /* Teal */
}

/* Dark mode */
[data-theme="dark"] {
    --lumina-adm-note: #60a5fa;
    --lumina-adm-tip: #34d399;
    --lumina-adm-warning: #fbbf24;
    --lumina-adm-warning-text: #f59e0b;
    --lumina-adm-danger: #f87171;
    --lumina-adm-important: #a78bfa;
    --lumina-adm-seealso: #2dd4bf;
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
