# Architecture

How the Sphinx Lumina Theme is structured internally.

## Theme Structure

```
src/sphinx_lumina_theme/
├── __init__.py              # Sphinx setup() hook, registers theme
├── locale/                  # gettext catalogs (sphinx.pot, <lang>/LC_MESSAGES/sphinx.po/.mo)
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

Font subsets and their `@font-face` declarations are generated from the original
WOFF2 files in `theme/static/fonts/`. After updating those originals, run
`uv run scripts/subset-fonts.py`, then `pnpm run build`. Commit the generated
`*-latin.woff2` files and `_static_src/css/fonts.css`; normal asset builds use
these checked-in files without requiring FontTools. The full fonts remain
available for characters outside the Latin subsets.

## Interactivity Pattern

Alpine.js components are registered via `Alpine.data()` in separate modules under `_static_src/js/`. Each component is imported and registered in `app.js`, then referenced in templates with `x-data`.

See {doc}`javascript-api` for the full component API reference.

An inline script measures the announcement before page content renders; the
announcement component keeps that measurement current with `ResizeObserver`. The shared
`--lumina-header-offset` includes this height, keeping content, sticky sidebars,
mobile navigation, and anchor targets clear of announcements that wrap on narrow
screens. Dismissing the banner restores the regular header offset.

The page outline's `scrollspy.js` measures the nested links to draw a continuous
SVG guide. It recalculates on resize to keep curves aligned with wrapped labels,
and marks the active link with `aria-current="location"`. Scroll updates select
the last section start above the anchor offset below the fixed header, using
one animation frame per update. The highlight and its dot animate together along
the curve, retargeting from their current position during rapid scrolling.
Reduced motion skips the animation. Without JavaScript,
the nested links keep a straight CSS guide.

### API disclosures

`api-disclosures.js` runs after the HTTP tools initialize. It adds disclosure buttons to Sphinx's Python, HTTP, and JavaScript signatures and toggles their definition bodies. It preserves links inside signatures, opens ancestor definitions for deep links, and reads the `api_expanded` theme option. Without JavaScript, definitions remain visible.

### HTTP request editor

`try-it.js` and `curl-copy.js` enhance the rendered `dl.http` endpoints. `_http-api-utils.js` extracts paths, fields, and HTTP request examples. At build time, `_tag_http_fields()` classes each httpdomain field name by its field type, such as `lumina-http-requestheader`, so the scripts find query parameters, headers, and JSON fields whatever language the labels use. A shared curl serializer handles both documentation templates and edited requests, with POSIX shell quoting.

The request panel keeps authentication in memory, shared by the normalized API base URL. It sends browser `fetch` requests with cookies omitted, redirects rejected, and cancellation through `AbortController`. It does not parse the original OpenAPI specification. The showcase uses sphinxcontrib-openapi's `httpdomain` renderer to preserve request schemas and examples.

### Mermaid diagrams

Mermaid rendering, theme changes, and fullscreen controls belong to `sphinxcontrib-mermaid`. Lumina’s `mermaid.js` observes rendered diagrams and records each SVG’s natural width; `mermaid.css` handles sizing, typography, and colors. The observer also handles SVG replacement after a theme change.

### Tables

`responsive-tables.js` wraps article tables in scrollable regions before Alpine
starts. Simple tables receive labels for the mobile layout. Tables with the
`lumina-table-interactive` class instead use the `tableControls` Alpine component
from `table-controls.js` for local filtering and sorting. It moves existing rows
to preserve their markup and state. Unsupported table structures remain static.
See {doc}`/reference/lists-and-tables` for the opt-in syntax.

## Search index and results

At `env-updated`, Lumina maps documents to their first root-toctree branch.
Configured `doc_sections` take precedence when rendering each page. The layout
emits a Pagefind section filter and plain-text parent titles as breadcrumb
metadata. These values are independent of the visible breadcrumb toggle.

The `doctree-resolved` hook adds unique `lumina-search-…` IDs to section headings
for Pagefind's sub-results. Existing section IDs and permalink URLs stay intact.
The `build-finished` hook indexes the rendered HTML as before.

The `searchModal` Alpine component loads available filters from Pagefind and
keys its bounded cache by query and scope. Request IDs discard outdated
responses, including responses arriving after the dialog closes. The dialog
lists up to ten pages with up to three heading links per page; all links share
one keyboard navigation sequence. Excerpts are sanitized before rendering.

## Translations

`setup()` registers `locale/` as an additional `sphinx` message catalog, so templates translate strings with the `_()` function that Sphinx provides. Sphinx's own translations and the project's `locale_dirs` take precedence over the bundled catalog.

JavaScript can't call gettext, so for non-English builds `layout.html` includes `components/i18n.html`, which renders every JavaScript string through `_()` into a `<script id="lumina-i18n" type="application/json">` block. `utils/i18n.js` exports `t(key, vars)`, which looks up that catalog and falls back to the English key; `app.js` exposes it to Alpine expressions as `$t`. See {doc}`translations` for the contributor workflow.

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
