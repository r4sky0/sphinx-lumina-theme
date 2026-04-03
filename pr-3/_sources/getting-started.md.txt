# Getting Started

Get Lumina running in your Sphinx project in under five minutes.

## Prerequisites

You need a working Sphinx project. If you don't have one yet:

```bash
mkdir my-docs && cd my-docs
uv init && uv add sphinx myst-parser
uv run sphinx-quickstart docs
```

Lumina requires **Python 3.10+** and **Sphinx 7.0+**.

## Installation

::::{tab-set}

:::{tab-item} uv (recommended)
```bash
uv add sphinx-lumina-theme@git+https://github.com/ralph089/sphinx-lumina-theme.git@v{version}
```
:::

:::{tab-item} pip
```bash
pip install git+https://github.com/ralph089/sphinx-lumina-theme.git@v{version}
```
:::

::::

## Minimal Configuration

Open your `conf.py` and set the theme:

```python
html_theme = "lumina"
```

That's it — Lumina works with zero configuration. Build your docs to see it:

```bash
uv run sphinx-build docs docs/_build/html
```

Open `docs/_build/html/index.html` in your browser.

## Recommended Configuration

Most projects will want a few more options. Here's a practical starting point:

```{code-block} python
:caption: conf.py
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

:::{tip}
See {doc}`customization` for the full list of theme options and CSS custom properties.
:::

## Using MyST Markdown

Lumina works with both reStructuredText and MyST Markdown. We recommend MyST for a more natural writing experience.

Install the parser and enable useful extensions:

```bash
uv add myst-parser
```

```{code-block} python
:caption: conf.py
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

### Pagefind (recommended)

[Pagefind](https://pagefind.app) provides fast, keyboard-driven search with no external services. Install it and run it after each build:

```bash
# Install Pagefind
npm install -g pagefind

# Build docs, then index
uv run sphinx-build docs docs/_build/html
pagefind --site docs/_build/html
```

:::{tip}
Automate this in a `Makefile`:
```makefile
docs:
	uv run sphinx-build docs docs/_build/html
	pagefind --site docs/_build/html
```
:::

### Built-in Sphinx search

If you prefer not to use Pagefind, switch to Sphinx's built-in search:

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

```bash
uv add sphinx-autobuild --dev
uv run sphinx-autobuild docs docs/_build/html --open-browser
```

This watches your `docs/` directory and automatically rebuilds when files change. Your browser refreshes automatically.

:::{note}
**Search during development:** Pagefind search requires a full build with indexing. During live preview, search will show a helpful message suggesting `Ctrl+F` instead. To enable full search:

```bash
uv run sphinx-build docs docs/_build/html
pagefind --site docs/_build/html
```
:::

:::{tip}
If you're also editing theme CSS or JavaScript source files, run the asset watcher in a separate terminal:
```bash
pnpm run dev
```
:::

## Next Steps

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Customization
:link: customization
:link-type: doc
Explore all theme options, accent colors, and CSS custom properties.
:::

:::{grid-item-card} Extensions
:link: extensions
:link-type: doc
Set up MyST, sphinx-design, Mermaid diagrams, and more.
:::

:::{grid-item-card} Reference
:link: reference/typography
:link-type: doc
Browse the complete reference for typography, admonitions, code blocks, and more.
:::

:::{grid-item-card} Troubleshooting
:link: troubleshooting
:link-type: doc
Solutions to common issues with builds, search, and styling.
:::

::::
