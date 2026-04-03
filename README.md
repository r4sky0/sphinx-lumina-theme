# Sphinx Lumina Theme

[![PyPI version](https://img.shields.io/pypi/v/sphinx-lumina-theme?color=%2310b981)](https://pypi.org/project/sphinx-lumina-theme/)
[![Python versions](https://img.shields.io/pypi/pyversions/sphinx-lumina-theme)](https://pypi.org/project/sphinx-lumina-theme/)
[![License](https://img.shields.io/github/license/r4sky0/sphinx-lumina-theme)](https://github.com/r4sky0/sphinx-lumina-theme/blob/main/LICENSE)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://r4sky0.github.io/sphinx-lumina-theme/)

A modern, clean Sphinx documentation theme built with **Tailwind CSS v4** and **Alpine.js**.

**[View the documentation →](https://r4sky0.github.io/sphinx-lumina-theme/)**

---

## Features

- **Dark mode** — automatic detection with manual toggle, zero FOUC
- **Responsive design** — mobile-first layout with collapsible sidebar
- **Full-text search** — modal-based search with keyboard navigation
- **Code highlighting** — syntax highlighting with one-click copy
- **Self-hosted fonts** — no external CDN dependencies

## Installation

```bash
uv add sphinx-lumina-theme@git+https://github.com/r4sky0/sphinx-lumina-theme.git@v{version}
```

or with pip:

```bash
pip install git+https://github.com/r4sky0/sphinx-lumina-theme.git@v{version}
```

Then in your `conf.py`:

```python
html_theme = "lumina"
```

For configuration options and customization, see the [documentation](https://r4sky0.github.io/sphinx-lumina-theme/).

## Development

```bash
git clone https://github.com/r4sky0/sphinx-lumina-theme.git
cd sphinx-lumina-theme
pnpm install        # JS dependencies
uv sync --extra dev # Python dependencies
pnpm run build      # Build assets
uv run pytest       # Run tests
```

## License

[MIT](LICENSE)
