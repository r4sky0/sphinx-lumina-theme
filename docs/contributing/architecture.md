# Architecture

How the Sphinx Lumina Theme is structured internally.

## Theme Structure

```
src/sphinx_lumina_theme/
├── __init__.py              # Sphinx setup() hook, registers theme
├── _static_src/             # SOURCE assets (edit these)
│   ├── css/                 # base.css imports admonitions/code/typography
│   └── js/                  # app.js is entry point, loads Alpine components
└── theme/                   # SPHINX THEME (templates + compiled assets)
    ├── layout.html          # Master template, extends basic/layout.html
    ├── theme.toml           # Theme config, options, inheritance
    ├── components/          # Jinja2 partials (header, sidebar, toc, etc.)
    └── static/              # Compiled CSS/JS + fonts (DO NOT edit directly)
```

:::{danger}
Never edit files in `theme/static/` directly — they are compiled outputs and **your edits will be overwritten** on the next build. Edit the sources in `_static_src/` and run `pnpm run build`.
:::

## Asset Build Pipeline

Source files in `_static_src/` are compiled into `theme/static/`:

JS
: esbuild bundles `_static_src/js/app.js` → `theme/static/lumina.js` (IIFE format)

CSS
: Tailwind CLI processes `_static_src/css/base.css` → `theme/static/lumina.css`

The build script is `scripts/build-assets.js`. Tailwind scans HTML templates and JS files for class usage.

```bash
pnpm run build          # Production build (minified, no sourcemaps)
pnpm run dev            # Watch mode (unminified, sourcemaps)
```

## Interactivity Pattern

Alpine.js components are registered via `Alpine.data()` in separate modules under `_static_src/js/`. Each component is imported and registered in `app.js`, then referenced in templates with `x-data`.

See {doc}`javascript-api` for the full component API reference.

## Theming

- CSS custom properties (`--lumina-accent`, `--lumina-bg`, `--lumina-text`, etc.) defined in `base.css`
- Dark mode toggled via `[data-theme="dark"]` attribute on `<html>`
- User preference persisted in `localStorage` key `lumina-theme`
- FOUC prevention: inline script in `layout.html` applies theme before paint

## Template Inheritance

The theme extends Sphinx's built-in `basic` theme. Templates use Jinja2 block inheritance — override blocks, don't replace the inheritance chain. The `!` prefix in `{% extends "!layout.html" %}` references the parent theme's template.

## Testing

Tests use pytest with BeautifulSoup for HTML assertions. The `build_output` fixture is session-scoped — it builds `tests/sample_docs/` once with Sphinx and returns the output path. Tests verify rendered HTML structure, not visual appearance.

```bash
uv run pytest -v                    # Verbose output
uv run pytest --tb=short            # Shorter tracebacks
```
