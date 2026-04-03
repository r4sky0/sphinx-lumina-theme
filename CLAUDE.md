# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A modern Sphinx documentation theme built with Tailwind CSS v4 and Alpine.js. Registered as the `lumina` theme via the `sphinx.html_themes` entry point.

## Commands

### Build Assets (CSS + JS)

```bash
pnpm run build          # Production build (minified, no sourcemaps)
pnpm run dev            # Watch mode (unminified, sourcemaps)
```

### Build Documentation

```bash
uv run sphinx-build docs docs/_build/html
```

### Run Tests

```bash
uv run pytest                       # All tests
uv run pytest tests/test_build.py   # Single file
uv run pytest -k test_name          # Single test by name
```

### Install Dependencies

```bash
pnpm install            # JS dependencies
uv sync --dev           # Python dependencies (includes dev extras)
```

## Architecture

### Asset Build Pipeline

Source files in `_static_src/` are compiled into `theme/static/`:

- **JS**: esbuild bundles `_static_src/js/app.js` → `theme/static/lumina.js` (IIFE format)
- **CSS**: Tailwind CLI processes `_static_src/css/base.css` → `theme/static/lumina.css`

The build script is `scripts/build-assets.js`. Tailwind scans HTML templates and JS files for class usage.

**You must run `pnpm run build` after changing any CSS or JS source files** — the compiled outputs in `theme/static/` are what Sphinx serves.

### Theme Structure

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

### Interactivity Pattern

Alpine.js components are registered via `Alpine.data()` in separate modules under `_static_src/js/`. Each component (scrollspy, themeToggle, searchModal, sidebar, headerLinks, copyPage) is imported and registered in `app.js`, then referenced in templates with `x-data`.

### Theming / Dark Mode

- CSS custom properties (`--lumina-accent`, `--lumina-bg`, `--lumina-text`, etc.) defined in `base.css`
- Dark mode toggled via `[data-theme="dark"]` attribute on `<html>`
- User preference persisted in `localStorage` key `lumina-theme`
- FOUC prevention: inline script in `layout.html`'s `extrahead` block applies theme before paint

### Testing

Tests use pytest with BeautifulSoup for HTML assertions. The `build_output` fixture (session-scoped) builds `tests/sample_docs/` with Sphinx and returns the output path. Tests verify rendered HTML structure, not visual appearance.

### Documentation

Docs are in `docs/` using MyST Markdown (not reStructuredText). The theme dogfoods itself — `conf.py` sets `html_theme = "lumina"`. Extensions: `myst_parser`, `sphinx_design`, `sphinx_copybutton`.

## Key Conventions

- **Package managers**: pnpm for JS, uv for Python — never use npm or pip
- **Fonts**: Self-hosted only (Source Sans 3, JetBrains Mono) — no external CDN links
- **Template inheritance**: Theme extends Sphinx's `basic` theme; override blocks, don't replace the inheritance chain
- **Design context**: See `.impeccable.md` for brand guidelines, design philosophy, and reference sites
