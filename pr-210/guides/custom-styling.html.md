# Custom Styling

Override CSS custom properties, fonts, syntax highlighting themes, and templates for deeper customization.

## Migrating to Lumina 2

Lumina 2 refreshes the default design. Existing theme options still work, but custom CSS and template overrides need review.

- **Page actions:** Copy Markdown and edit links now live in the page-actions menu. Reading time appears below the introduction with a clock icon. Overrides of `layout.html` or `components/toc.html` should use the new `components/page-actions.html` component.
- **Link colors:** `--lumina-accent` controls brand accents; `--lumina-link` controls readable text links and focus outlines. Set both for each mode if you customize tokens directly. The `accent_color` option derives both automatically.
- **Surfaces:** `--lumina-navigation-bg` and `--lumina-floating-bg` control the sidebar and floating menus separately from the page background.
- **Content:** Cards no longer lift or cast shadows; admonitions use a thin border on all sides. Heading sizes, weights, and spacing have changed.
- **Mobile navigation:** The page outline is now available below the breadcrumbs. `show_toc = "false"` hides both desktop and mobile outlines.

Rebuild your docs and check custom styles in both color modes, including mobile layouts. Use `html_short_title` for a shorter header label without changing your Sphinx project name.

## Adding a Custom Stylesheet

Create a CSS file and register it in your `conf.py`:

```python
html_static_path = ["_static"]
html_css_files = ["custom.css"]
```

Then create `docs/_static/custom.css` with your overrides.

## CSS Custom Properties

Lumina defines CSS custom properties for all visual tokens. Override them in your custom stylesheet. For a complete reference of every token, default value, and what each one controls, see [CSS Variables](../reference/css-variables.md).

### Core Colors

```css
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

Latin text uses smaller font subsets. The browser loads the original full fonts
when other characters are needed, preserving the existing language coverage.

To use your own fonts, load them from your docs or a font provider, then set the `--lumina-font-sans` and `--lumina-font-mono` tokens. The theme applies them everywhere, including code blocks, API documentation and diagrams.

### Local font files

Host a font with your docs when you want a font that isn’t on Google Fonts, or when readers’ browsers shouldn’t contact a third party. This example uses a font called `My Font` with regular and bold files.

1. Copy the `.woff2` files into your static directory:
   ```text
   docs/
   ├── conf.py
   └── _static/
       ├── custom.css
       └── fonts/
           ├── my-font-regular.woff2
           └── my-font-bold.woff2
   ```
2. Register the stylesheet in `conf.py`:
   ```python
   html_static_path = ["_static"]
   html_css_files = ["custom.css"]
   ```
3. Declare each file with `@font-face`, then point Lumina at the font:
   ```css
   @font-face {
       font-family: "My Font";
       src: url("fonts/my-font-regular.woff2") format("woff2");
       font-weight: 400;
       font-display: swap;
   }

   @font-face {
       font-family: "My Font";
       src: url("fonts/my-font-bold.woff2") format("woff2");
       font-weight: 700;
       font-display: swap;
   }

   :root {
       --lumina-font-sans: "My Font", system-ui, sans-serif;
   }
   ```
4. Rebuild your docs. Pages now use `My Font` for body text.

To change the code font, set `--lumina-font-mono` the same way.

Keep these details in mind:

- **Paths:** `url()` paths are relative to the CSS file, not to `conf.py`.
- **Weights:** Lumina uses weights 400, 500, 600 and 700 for body text. If a weight is missing, the browser uses the closest one or synthesizes bold.
- **Variable fonts:** one file can cover every weight. Declare it with `font-weight: 400 700;`.
- **Missing fonts:** if a page still shows the system font, check the browser’s Network tab for a 404 on the `.woff2` file, and check that the `font-family` name matches in both places.

### Other font providers, e.g. Google Fonts

Add the provider’s stylesheet to `html_css_files`, then set the font tokens in your custom CSS. This example loads Inter and Fira Code from [Google Fonts](https://fonts.google.com/):

```python
html_static_path = ["_static"]
html_css_files = [
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap",
    "custom.css",
]
```

```css
:root {
    --lumina-font-sans: "Inter", system-ui, sans-serif;
    --lumina-font-mono: "Fira Code", ui-monospace, monospace;
}
```

#### WARNING
With a hosted font, readers’ browsers contact the provider, which receives their IP address. Check whether this affects your privacy policy or GDPR obligations.

## Hyphenation

Paragraphs fill the center column and wrap at spaces. Long unbroken text, such as URLs, can wrap to prevent overflow.

To let the browser hyphenate words at language-appropriate points, add this to your custom stylesheet:

```css
.lumina-article {
    -webkit-hyphens: auto;
    hyphens: auto;
}
```

Set the document language in `conf.py` so Sphinx emits the matching HTML `lang` attribute:

```python
language = "en"  # Use "de" for German, for example.
```

Hyphenation depends on the browser’s dictionaries for that language. Lumina excludes code and keyboard shortcuts from hyphenation. Use `manual` instead of `auto` in both declarations to return to author-supplied soft hyphens only.

## Syntax Highlighting

Lumina ships five syntax highlighting presets — curated light/dark pairs tested for contrast on the theme’s code block backgrounds. Set the `code_style` theme option to switch:

```python
html_theme_options = {
    "code_style": "nord",
}
```

#### Available presets

| Preset       | Light style   | Dark style   | Character                                      |
|--------------|---------------|--------------|------------------------------------------------|
| `"default"`  | default       | monokai      | Neutral baseline — familiar Pygments defaults  |
| `"nord"`     | tango         | nord         | Cool, crisp, precise — arctic calm             |
| `"one-dark"` | friendly      | one-dark     | Warm, modern — Atom’s popular syntax theme     |
| `"gruvbox"`  | gruvbox-light | gruvbox-dark | Earthy, bold — retro groove with warm tones    |
| `"material"` | lovelace      | material     | Refined, editorial — Google’s Material palette |

### Custom styles

For full control, set `pygments_style` and `pygments_dark_style` directly in `conf.py`. When either is set, the `code_style` preset is ignored.

```python
pygments_style = "friendly"
pygments_dark_style = "dracula"
```

## Hiding Page Elements

Selectively hide UI elements globally or per-page.

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

Lumina’s templates are designed for extension. To override a specific component, create a `_templates/` directory:

```python
templates_path = ["_templates"]
```

Then create a template that extends the original:

```html+jinja
{% extends "!layout.html" %}

{% block extrahead %}
{{ super() }}
<link rel="stylesheet" href="{{ pathto('_static/custom.css', 1) }}">
{% endblock %}
```

The `!` prefix tells Sphinx to use the theme’s original template as the base, so you only override the blocks you need.
