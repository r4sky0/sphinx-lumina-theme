---
myst:
  html_meta:
    description: "Complete reference of all CSS custom properties (theme tokens) Lumina exposes for customization."
---

# CSS Variables

Every visual surface in Lumina is driven by a CSS custom property. Override any of these in your own stylesheet to retheme the docs without forking the theme. For step-by-step instructions on adding a custom stylesheet, see {doc}`/guides/custom-styling`.

All tokens are defined for both the default light scope (`:root` / `[data-theme="light"]`) and dark mode (`[data-theme="dark"]`).

## Theme tokens

The core surface and text tokens. These are the variables you'll override most often.

```{list-table}
:header-rows: 1
:widths: 28 22 22 28

* - Token
  - Light default
  - Dark default
  - What it affects
* - `--lumina-bg`
  - `#fcfcfc`
  - `#09090b`
  - Page background, modal background
* - `--lumina-bg-secondary`
  - `#f4f4f5`
  - `#18181b`
  - Sidebar fill, hover surfaces, table-header tint
* - `--lumina-text`
  - `#18181b`
  - `#fafafa`
  - Body and heading color
* - `--lumina-text-muted`
  - `#52525b`
  - `#a1a1aa`
  - Secondary text (TOC links, captions, footer)
* - `--lumina-border`
  - `#e4e4e7`
  - `#27272a`
  - Dividers, table cell borders, sidebar separators
* - `--lumina-accent`
  - `#10b981`
  - `#10b981`
  - Links, focus ring, active TOC indicator, skip link, headerlink tooltip. Also overridable through the `accent_color` theme option.
* - `--lumina-accent-light`
  - `#ecfdf5`
  - `#022c22`
  - Hover/active background tint for accent surfaces (current sidebar item, copy-page hover)
* - `--lumina-code-bg`
  - `#f4f4f5`
  - `#1c1c20`
  - Inline code and code block background
```

:::{tip}
Set the accent through the theme option rather than overriding the variable directly — `accent_color` also derives `--lumina-accent-light` automatically using `color-mix()`. Override the variable directly only when you need a different tint than the auto-derived one.
:::

## Admonition tokens

One color per admonition type, plus a darker variant for the warning text where the regular hue would clip on light backgrounds.

```{list-table}
:header-rows: 1
:widths: 32 22 22 24

* - Token
  - Light default
  - Dark default
  - Used by
* - `--lumina-adm-note`
  - `#3b82f6`
  - `#60a5fa`
  - `note`
* - `--lumina-adm-tip`
  - `#10b981`
  - `#34d399`
  - `tip`, `hint`
* - `--lumina-adm-warning`
  - `#f59e0b`
  - `#fbbf24`
  - `warning`, `caution`, `attention`
* - `--lumina-adm-warning-text`
  - `#d97706`
  - `#f59e0b`
  - Warning title text (darker for AA contrast on light background)
* - `--lumina-adm-danger`
  - `#ef4444`
  - `#f87171`
  - `danger`, `error`
* - `--lumina-adm-important`
  - `#8b5cf6`
  - `#a78bfa`
  - `important`
* - `--lumina-adm-seealso`
  - `#14b8a6`
  - `#2dd4bf`
  - `seealso`
```

The visible left border, icon mask, and 5–8 % background tint of every admonition derive from these single colors via `color-mix()` — overriding the token recolors the whole admonition.

## sphinx-design tokens

Lumina also overrides sphinx-design's color tokens (`--sd-color-primary`, `--sd-color-info`, etc.) so cards, buttons, and badges from `sphinx_design` blend with the rest of the theme. These are documented in [the sphinx-design reference](https://sphinx-design.readthedocs.io/en/latest/css_variables.html); Lumina's defaults map them onto its own palette.

If you want sphinx-design components to follow your accent color, override them alongside the Lumina tokens:

```css
:root,
html:root {
  --lumina-accent: #6366f1;
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
  --lumina-accent-light: #500724;
}
```

## Where each token is wired up

Every token is consumed in `src/sphinx_lumina_theme/_static_src/css/`. If you're customizing deeply and want to know exactly where a token is read, the easiest reference is the source — `base.css` declares the tokens; the per-feature stylesheets (`typography.css`, `code.css`, `admonitions.css`, `api.css`, `landing.css`, `mermaid.css`) consume them via `var(--…)`.

For non-color customization (fonts, page elements, syntax highlighting), see {doc}`/guides/custom-styling`.
