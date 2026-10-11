# CSS Variables

Every visual surface in Lumina is driven by a CSS custom property. Override any of these in your own stylesheet to retheme the docs without forking the theme. For step-by-step instructions on adding a custom stylesheet, see [Custom Styling](../guides/custom-styling.md).

All tokens are defined for both the default light scope (`:root` / `[data-theme="light"]`) and dark mode (`[data-theme="dark"]`).

## Theme tokens

The core surface and text tokens. These are the variables you’ll override most often.

| Token                    | Light default   | Dark default   | What it affects                                                                                                            |
|--------------------------|-----------------|----------------|----------------------------------------------------------------------------------------------------------------------------|
| `--lumina-bg`            | `#fdfdfc`       | `#151918`      | Page background                                                                                                            |
| `--lumina-bg-secondary`  | `#f4f5f4`       | `#202623`      | Hover surfaces and table-header tint                                                                                       |
| `--lumina-text`          | `#202624`       | `#e9eeeb`      | Body and heading color                                                                                                     |
| `--lumina-text-muted`    | `#59635e`       | `#a8b5ac`      | Secondary text (TOC links, captions, footer)                                                                               |
| `--lumina-border`        | `#dfe5e1`       | `#303b34`      | Dividers, table cell borders, sidebar separators                                                                           |
| `--lumina-accent`        | `#10b981`       | `#10b981`      | Brand accents, active indicators, skip link, headerlink tooltip. Also overridable through the `accent_color` theme option. |
| `--lumina-link`          | `#08764f`       | `#5ed9a3`      | Readable text links and focus outlines                                                                                     |
| `--lumina-navigation-bg` | `#f7f8f6`       | `#111613`      | Desktop sidebar surface and the outer gutter to its left                                                                   |
| `--lumina-floating-bg`   | `#fdfdfc`       | `#242c27`      | Section switcher, page-actions menu, search dialog, and back-to-top button                                                 |
| `--lumina-accent-light`  | `#eaf6ef`       | `#1c3329`      | Hover/active background tint for accent surfaces, including the current sidebar item                                       |
| `--lumina-code-bg`       | `#f6f7f6`       | `#1b211e`      | Inline code and code block background                                                                                      |

## Admonition tokens

One color per admonition type, plus a darker variant for the warning text where the regular hue would clip on light backgrounds.

| Token                       | Light default   | Dark default   | Used by                                                         |
|-----------------------------|-----------------|----------------|-----------------------------------------------------------------|
| `--lumina-adm-note`         | `#2563eb`       | `#60a5fa`      | `note`                                                          |
| `--lumina-adm-tip`          | `#08764f`       | `#34d399`      | `tip`, `hint`                                                   |
| `--lumina-adm-warning`      | `#f59e0b`       | `#fbbf24`      | `warning`, `caution`, `attention`                               |
| `--lumina-adm-warning-text` | `#b45309`       | `#f59e0b`      | Warning title text (darker for AA contrast on light background) |
| `--lumina-adm-danger`       | `#dc2626`       | `#f87171`      | `danger`, `error`                                               |
| `--lumina-adm-important`    | `#7c3aed`       | `#a78bfa`      | `important`                                                     |
| `--lumina-adm-seealso`      | `#0e7490`       | `#22d3ee`      | `seealso`                                                       |

The thin border, icon mask, and 4–5% background tint of every admonition derive from these colors via `color-mix()` — overriding the token recolors the whole admonition.

## sphinx-design tokens

Lumina also overrides sphinx-design’s color tokens (`--sd-color-primary`, `--sd-color-info`, etc.) so cards, buttons, and badges from `sphinx_design` blend with the rest of the theme. These are documented in [the sphinx-design reference](https://sphinx-design.readthedocs.io/en/latest/css_variables.html); Lumina’s defaults map them onto its own palette.

If you want sphinx-design components to follow your accent color, override them alongside the Lumina tokens:

```css
:root,
html:root {
  --lumina-accent: #6366f1;
  --lumina-link: #4f46e5;
  --sd-color-primary: #6366f1;
  --sd-color-primary-highlight: #4f46e5;
}
```

## Override patterns

### Switch the entire palette

```css
:root {
  --lumina-bg: #fffaf2;
  --lumina-bg-secondary: #faf3e7;
  --lumina-text: #1c1917;
  --lumina-text-muted: #57534e;
  --lumina-border: #e7e5e4;
  --lumina-accent: #ea580c;
  --lumina-link: #c2410c;
  --lumina-navigation-bg: #faf3e7;
  --lumina-floating-bg: #fffaf2;
  --lumina-accent-light: #fff7ed;
  --lumina-code-bg: #faf3e7;
}
```

### Recolor a single admonition type

```css
:root {
  --lumina-adm-note: #6366f1; /* Indigo notes everywhere */
}

[data-theme="dark"] {
  --lumina-adm-note: #818cf8;
}
```

### Match a brand color in dark mode only

```css
[data-theme="dark"] {
  --lumina-accent: #f472b6;
  --lumina-link: #f9a8d4;
  --lumina-accent-light: #500724;
}
```

## Where each token is wired up

Every token is consumed in `src/sphinx_lumina_theme/_static_src/css/`. If you’re customizing deeply and want to know exactly where a token is read, the easiest reference is the source — `base.css` declares the tokens; the per-feature stylesheets (`typography.css`, `code.css`, `admonitions.css`, `api.css`, `landing.css`, `mermaid.css`) consume them via `var(--…)`.

For non-color customization (fonts, page elements, syntax highlighting), see [Custom Styling](../guides/custom-styling.md).
