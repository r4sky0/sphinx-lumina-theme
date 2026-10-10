# Installation

Install the Lumina theme and build your first page.

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

Lumina requires **Python 3.12+** and **Sphinx 8.0+**.

## Install the Theme

### uv (recommended)

```bash
uv add sphinx-lumina-theme
```

### pip

```bash
pip install sphinx-lumina-theme
```

## First Build

Open your `conf.py` and set the theme:

```python
html_theme = "lumina"
```

That’s it — Lumina works with zero configuration. Build your docs:

### uv (recommended)

```bash
uv run sphinx-build docs docs/_build/html
```

### pip

```bash
sphinx-build docs docs/_build/html
```

Open `docs/_build/html/index.html` in your browser.

## Next Steps

You’ve got Lumina running. Next, tune it for your project or explore what it can do.

Explore all theme options, accent colors, and the recommended setup.

Set up search, dark mode, MyST Markdown, navigation, and more.

Browse the complete reference for typography, admonitions, code blocks, and more.
