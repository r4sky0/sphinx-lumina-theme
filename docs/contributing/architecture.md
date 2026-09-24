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
pnpm run build:icons    # Regenerate Python Lucide icon definitions
```

## Interactivity Pattern

Alpine.js components are registered via `Alpine.data()` in separate modules under `_static_src/js/`. Each component is imported and registered in `app.js`, then referenced in templates with `x-data`.

See {doc}`javascript-api` for the full component API reference.

The page outline's `scrollspy.js` measures the nested links to draw a continuous
SVG guide. It recalculates on resize to keep curves aligned with wrapped labels,
and marks the active link with `aria-current="location"`. Without JavaScript,
the nested links keep a straight CSS guide.

### API disclosures

`api-disclosures.js` runs after the HTTP tools initialize. It adds disclosure buttons to Sphinx's Python, HTTP, and JavaScript signatures and toggles their definition bodies. It preserves links inside signatures, opens ancestor definitions for deep links, and reads the `api_expanded` theme option. Without JavaScript, definitions remain visible.

### HTTP request editor

`try-it.js` and `curl-copy.js` enhance the rendered `dl.http` endpoints. `_http-api-utils.js` extracts paths, fields, and HTTP request examples. A shared curl serializer handles both documentation templates and edited requests, with POSIX shell quoting.

The request panel keeps authentication in memory, shared by the normalized API base URL. It sends browser `fetch` requests with cookies omitted, redirects rejected, and cancellation through `AbortController`. It does not parse the original OpenAPI specification. The showcase uses sphinxcontrib-openapi's `httpdomain` renderer to preserve request schemas and examples.

### Mermaid diagrams

Mermaid rendering, theme changes, and fullscreen controls belong to `sphinxcontrib-mermaid`. Lumina’s `mermaid.js` observes rendered diagrams and records each SVG’s natural width; `mermaid.css` handles sizing, typography, and colors. The observer also handles SVG replacement after a theme change.

## Theming

- CSS custom properties (`--lumina-accent`, `--lumina-bg`, `--lumina-text`, etc.) defined in `base.css`. See {doc}`/reference/css-variables` for the full token reference.
- The same tokens are exposed as Tailwind v4 theme colors via an `@theme inline` block in `base.css`, so templates use named utilities (`bg-lumina-bg`, `text-lumina-text-muted`, `border-lumina-border`) rather than `bg-[var(--lumina-bg)]`. Add a new entry to that block when introducing a new token you want available as a Tailwind utility.
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
