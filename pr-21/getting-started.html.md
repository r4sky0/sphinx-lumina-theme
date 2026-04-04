# Getting Started

Get Lumina running in your Sphinx project in under five minutes.

## Prerequisites

You need a working Sphinx project. If you don’t have one yet:

### uv (recommended)

```bash
mkdir my-docs && cd my-docs
uv init && uv add sphinx myst-parser
uv run sphinx-quickstart docs
```

### pip

```bash
mkdir my-docs && cd my-docs
python -m venv .venv && source .venv/bin/activate
pip install sphinx myst-parser
sphinx-quickstart docs
```

Lumina requires **Python 3.10+** and **Sphinx 8.0+**.

## Installation

### uv (recommended)

```bash
uv add sphinx-lumina-theme@git+https://github.com/r4sky0/sphinx-lumina-theme.git@v1.9.0
```

### pip

```bash
pip install git+https://github.com/r4sky0/sphinx-lumina-theme.git@v1.9.0
```

## Minimal Configuration

Open your `conf.py` and set the theme:

```python
html_theme = "lumina"
```

That’s it — Lumina works with zero configuration. Build your docs to see it:

### uv (recommended)

```bash
uv run sphinx-build docs docs/_build/html
```

### pip

```bash
sphinx-build docs docs/_build/html
```

Open `docs/_build/html/index.html` in your browser.

## Recommended Configuration

Most projects will want a few more options. Here’s a practical starting point:

```python
extensions = [
    "myst_parser",           # Write docs in Markdown
    "sphinx_design",         # Cards, grids, tabs, badges
    "sphinx_copybutton",     # Copy button on code blocks
]

html_theme = "lumina"
html_theme_options = {
    "accent_color": "#10b981",                                          # Emerald (default)
    "source_repository": "https://github.com/you/your-project",        # Enables "Edit on GitHub"
    "source_branch": "main",
    "source_directory": "docs/",
}
```

## Using MyST Markdown

Lumina works with both reStructuredText and MyST Markdown. We recommend MyST for a more natural writing experience.

Install the parser and enable useful extensions:

### uv (recommended)

```bash
uv add myst-parser
```

### pip

```bash
pip install myst-parser
```

```python
extensions = ["myst_parser"]

myst_enable_extensions = [
    "colon_fence",    # ::: directive syntax (cleaner than ```)
    "dollarmath",     # $inline$ and $$display$$ math
    "tasklist",       # - [x] task list checkboxes
    "deflist",        # Definition lists
    "fieldlist",      # :Field: value metadata
    "substitution",   # {{variable}} replacements
]
```

Then write your docs in `.md` files instead of `.rst`:

```markdown
# My Page Title

This is a paragraph with **bold** and `code`.

:::{note}
Admonitions use the colon fence syntax.
:::
```

## Setting Up Search

Lumina supports two search backends:

### Pagefind (default)

[Pagefind](https://pagefind.app) provides fast, keyboard-driven search with no external services. Lumina runs Pagefind automatically at the end of each build — no manual setup required. You just need [Node.js](https://nodejs.org) installed so that `npx` is available.

Build your docs and search is ready:

### uv (recommended)

```bash
uv run sphinx-build docs docs/_build/html
```

### pip

```bash
sphinx-build docs docs/_build/html
```

### Built-in Sphinx search

If you prefer not to use Pagefind, switch to Sphinx’s built-in search:

```python
html_theme_options = {
    "search_backend": "sphinx",
}
```

The built-in search works without any additional setup but is slower and less featured.

## Adding Navigation Links

Add links to your site header for quick access to key pages:

```python
html_theme_options = {
    "nav_links": [
        {"title": "Guide", "url": "getting-started"},
        {"title": "API", "url": "api/index"},
        {"title": "GitHub", "url": "https://github.com/you/your-project", "external": True},
    ],
}
```

## Adding Social Links

Display icon links in the header (currently supports GitHub):

```python
html_theme_options = {
    "social_links": [
        {"icon": "github", "url": "https://github.com/you/your-project"},
    ],
}
```

## Dark Mode

Lumina includes dark mode out of the box. Readers can toggle between light, dark, and system preference using the button in the header.

To change the default:

```python
html_theme_options = {
    "dark_mode_default": "auto",   # "auto", "light", or "dark"
}
```

## Development Workflow

For a live-reloading development experience, use `sphinx-autobuild`:

### uv (recommended)

```bash
uv add sphinx-autobuild --dev
uv run sphinx-autobuild docs docs/_build/html --open-browser
```

### pip

```bash
pip install sphinx-autobuild
sphinx-autobuild docs docs/_build/html --open-browser
```

This watches your `docs/` directory and automatically rebuilds when files change. Your browser refreshes automatically.

#### NOTE
**Search during development:** Pagefind indexes your content during full builds. During live preview with `sphinx-autobuild`, search may not be available. Use `⌘F` / `Ctrl+F` for in-page search instead.

## Next Steps

Explore all theme options, accent colors, and CSS custom properties.

Set up MyST, sphinx-design, Mermaid diagrams, and more.

Browse the complete reference for typography, admonitions, code blocks, and more.
