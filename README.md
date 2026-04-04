# Sphinx Lumina Theme

[![PyPI version](https://img.shields.io/pypi/v/sphinx-lumina-theme?color=%2310b981)](https://pypi.org/project/sphinx-lumina-theme/)
[![Python versions](https://img.shields.io/pypi/pyversions/sphinx-lumina-theme)](https://pypi.org/project/sphinx-lumina-theme/)
[![License](https://img.shields.io/github/license/r4sky0/sphinx-lumina-theme)](https://github.com/r4sky0/sphinx-lumina-theme/blob/main/LICENSE)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://r4sky0.github.io/sphinx-lumina-theme/)

A modern Sphinx theme that treats documentation as a first-class product experience. Clean typography, responsive layout, dark mode, and instant search — out of the box.

<a href="https://r4sky0.github.io/sphinx-lumina-theme/">
  <img src="docs/assets/demo.gif" alt="Sphinx Lumina Theme — Quick tour showing light and dark mode, sidebar navigation, content area with code blocks, and table of contents" width="100%">
</a>

<p align="center">
  <a href="https://r4sky0.github.io/sphinx-lumina-theme/"><strong>Documentation</strong></a>
</p>

## Features

- **Dark mode** — follows system preference with manual toggle, no flash of unstyled content
- **Instant search** — Pagefind-powered search with keyboard navigation (`⌘K`)
- **Responsive layout** — mobile-first with collapsible sidebar and sticky table of contents
- **MyST Markdown** — write docs in Markdown with full Sphinx directive support
- **Interactive HTTP API** — OpenAPI endpoint docs with live "Try it out" panels and curl copy buttons; no Swagger UI needed
- **Code blocks** — syntax highlighting with one-click copy
- **Self-hosted fonts** — Source Sans 3 and JetBrains Mono, no external CDN calls
- **Customizable** — accent colors, navigation links, social links, and more via `conf.py`

## Quick Start

Requires **Python 3.10+** and **Sphinx 8.0+**.

```bash
uv add sphinx-lumina-theme@git+https://github.com/r4sky0/sphinx-lumina-theme.git@v{version}
```

Set the theme in your `conf.py`:

```python
html_theme = "lumina"
```

Build your docs:

```bash
uv run sphinx-build docs docs/_build/html
```

That's it. For pip, MyST Markdown setup, and configuration options, see the [Getting Started](https://r4sky0.github.io/sphinx-lumina-theme/getting-started.html) guide.

## HTTP API Documentation

Set `api_base_url` in your theme options to add interactive features to every documented HTTP endpoint:

```python
html_theme_options = {
    "api_base_url": "https://api.example.com/v1",
}
```

- **Copy as curl** — a button on every endpoint signature copies a ready-to-run `curl` command to the clipboard
- **Try it out** — a collapsible panel lets readers fill in parameters and send live requests from the docs page
- **Per-block override** — wrap endpoints in `<div data-api-base-url="...">` to use a different server for a specific group

Works with both [`sphinxcontrib-openapi`](https://sphinxcontrib-openapi.readthedocs.io/) (auto-generated from spec files) and manually written `sphinxcontrib-httpdomain` directives.

## Configuration

All options go in `html_theme_options` in your `conf.py`. Every option has a sensible default — you only need to set what you want to change.

```python
html_theme_options = {
    "accent_color": "#10b981",
    "dark_mode_default": "auto",       # "auto", "light", or "dark"
    "nav_links": "Guide=/guide, API=/api",
    "source_repository": "https://github.com/you/your-repo",
    "social_links": "github=https://github.com/you",
    "api_base_url": "https://api.example.com/v1",  # enables interactive API features
}
```

See the full [Configuration](https://r4sky0.github.io/sphinx-lumina-theme/getting-started/configuration.html) reference for all available options.

## Development

```bash
git clone https://github.com/r4sky0/sphinx-lumina-theme.git
cd sphinx-lumina-theme
pnpm install        # JS dependencies
uv sync --extra dev # Python dependencies
pnpm run build      # Build CSS + JS assets
uv run pytest       # Run tests
```

## License

[MIT](LICENSE)
