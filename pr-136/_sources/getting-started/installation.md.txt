# Installation

Install the Lumina theme and build your first page.

## Prerequisites

You need a working Sphinx project. If you don't have one yet:

::::{tab-set}

:::{tab-item} uv (recommended)
```bash
mkdir my-docs && cd my-docs
uv init && uv add sphinx myst-parser
uv run sphinx-quickstart docs
```
:::

:::{tab-item} pip
```bash
mkdir my-docs && cd my-docs
python -m venv .venv && source .venv/bin/activate
pip install sphinx myst-parser
sphinx-quickstart docs
```
:::

::::

Lumina requires **Python 3.12+** and **Sphinx 8.0+**.

## Install the Theme

::::{tab-set}

:::{tab-item} uv (recommended)
```bash
uv add sphinx-lumina-theme
```
:::

:::{tab-item} pip
```bash
pip install sphinx-lumina-theme
```
:::

::::

## First Build

Open your `conf.py` and set the theme:

```{code-block} python
:caption: conf.py
html_theme = "lumina"
```

That's it — Lumina works with zero configuration. Build your docs:

::::{tab-set}

:::{tab-item} uv (recommended)
```bash
uv run sphinx-build docs docs/_build/html
```
:::

:::{tab-item} pip
```bash
sphinx-build docs docs/_build/html
```
:::

::::

Open `docs/_build/html/index.html` in your browser.

:::{tip}
Press {kbd}`⌘K` / {kbd}`Ctrl+K` to search your docs once Pagefind has indexed them. Search works after a full build — see {doc}`/guides/search` for details.
:::

## Next Steps

You've got Lumina running. Next, tune it for your project or explore what it can do.

::::{grid} 1 1 2 3
:gutter: 3

:::{grid-item-card} Configuration
:link: configuration
:link-type: doc
:icon: sliders-horizontal
:icon-style: featured
Explore all theme options, accent colors, and the recommended setup.
:::

:::{grid-item-card} Guides
:link: /guides/index
:link-type: doc
:icon: book-open
:icon-style: featured
Set up search, dark mode, MyST Markdown, navigation, and more.
:::

:::{grid-item-card} Reference
:link: /reference/index
:link-type: doc
:icon: list
:icon-style: featured
Browse the complete reference for typography, admonitions, code blocks, and more.
:::

::::
