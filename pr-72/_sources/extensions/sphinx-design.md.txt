# sphinx-design

[sphinx-design](https://sphinx-design.readthedocs.io/) adds cards, grids, tabs, badges, buttons, and dropdowns. Lumina styles all of these components with its own design language.

## Setup

```bash
uv add sphinx-design
```

```{code-block} python
:caption: conf.py
extensions = ["sphinx_design"]
```

## What You Get

::::{grid} 1 1 2 3
:gutter: 3

:::{grid-item-card} Cards
Contained content blocks with optional headers, footers, and links.

See {doc}`/reference/cards-and-grids`
:::

:::{grid-item-card} Grids
Responsive layouts with configurable columns per breakpoint.

See {doc}`/reference/cards-and-grids`
:::

:::{grid-item-card} Tabs
Tabbed content panels for grouping related information.

See {doc}`/reference/code-blocks`
:::

:::{grid-item-card} Badges
Inline status labels with color variants.

See {doc}`/reference/badges-and-buttons`
:::

:::{grid-item-card} Buttons
Styled link buttons with primary and secondary variants.

See {doc}`/reference/badges-and-buttons`
:::

:::{grid-item-card} Dropdowns
Collapsible content sections.

See {doc}`/reference/admonitions`
:::

::::
