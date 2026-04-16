# Icons

Make your docs easier to scan by adding icons to cards, sidebar navigation, and your site logo. Lumina includes all 1900+ [Lucide](https://lucide.dev/icons/) icons — rendered as inline SVG at build time with zero runtime cost.

:::{tip}
Not sure what's available? The {doc}`/reference/icons` page has an interactive browser — search by name and click any icon to copy it.
:::

## Card Icons

Add an `:icon:` option to any `{card}` or `{grid-item-card}` directive:

````{code-block} markdown
:caption: docs/index.md

:::{card} Getting Started
:icon: rocket

Install and configure Lumina in minutes.
:::
````

**Result:**

:::{card} Getting Started
:icon: rocket

Install and configure Lumina in minutes.
:::

### Featured Style

For landing pages or feature showcases, the **featured** style places a larger icon in a tinted pill above the title:

````{code-block} markdown
:caption: docs/index.md

:::{card} Getting Started
:icon: rocket
:icon-style: featured

Install and configure Lumina in minutes.
:::
````

**Result:**

:::{card} Getting Started
:icon: rocket
:icon-style: featured

Install and configure Lumina in minutes.
:::

### Grid Cards

Both styles work with `{grid-item-card}`:

::::{grid} 1 1 2 3
:gutter: 3

:::{grid-item-card} Guides
:icon: book-open
:icon-style: featured
Step-by-step tutorials.
:::

:::{grid-item-card} Reference
:icon: list
:icon-style: featured
API documentation.
:::

:::{grid-item-card} FAQ
:icon: circle-help
:icon-style: featured
Common questions.
:::

::::

### Options Reference

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `:icon:` | Any Lucide icon name | — | Icon to display on the card |
| `:icon-style:` | `inline`, `featured` | `inline` | `inline` places the icon next to the title. `featured` shows a larger icon in a tinted pill above it. |

Cards without `:icon:` render exactly as before.

## Sidebar Icons

Add an `icon` field to a page's frontmatter to display it in the sidebar:

````{code-block} yaml
:caption: docs/getting-started/index.md

---
icon: rocket
---
# Getting Started
````

The icon appears next to the page title in the sidebar. Pages without an `icon` field are unaffected — no empty space, no layout shift.

:::{tip}
Sidebar icons work best on top-level section pages. Adding icons to every nested page creates visual clutter.
:::

## Logo Icon

Use a Lucide icon as your site logo instead of a custom image:

```{code-block} python
:caption: conf.py

html_theme_options = {
    "logo_icon": "hexagon",
}
```

The icon renders in your accent color and adapts to both light and dark mode automatically.

`logo_icon` is only used when no image logo is configured. If you set `html_logo`, `light_logo`, or `dark_logo`, those take precedence.

## Finding Icon Names

Use the {doc}`Icon Browser </reference/icons>` to search all 1900+ icons and click to copy names.

Icon names use **kebab-case** — the same format shown on [lucide.dev/icons](https://lucide.dev/icons/):

| Example | Name |
|---------|------|
| Rocket | `rocket` |
| Book Open | `book-open` |
| Circle Help | `circle-help` |
| Hexagon | `hexagon` |
| Sparkles | `sparkles` |

If you use an icon name that doesn't exist, the build continues without errors — the icon is silently omitted.
