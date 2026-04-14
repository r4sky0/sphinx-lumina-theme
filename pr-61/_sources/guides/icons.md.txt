# Icons

Add [Lucide](https://lucide.dev/icons/) icons to cards, sidebar navigation, and your site logo.

Lumina ships with the full Lucide icon set (1900+ icons). Icons render as inline SVG at build time — no JavaScript, no external requests, no layout shift.

## Card Icons

Add an icon to any `{card}` or `{grid-item-card}` directive with the `:icon:` option:

````{code-block} markdown
:caption: docs/index.md

:::{card} Getting Started
:icon: rocket

Install and configure Lumina in minutes.
:::
````

Here's how that renders:

:::{card} Getting Started
:icon: rocket

Install and configure Lumina in minutes.
:::

By default, icons appear **inline** next to the card title. For a more prominent treatment, use the **featured** style — a larger icon in a tinted accent pill above the title:

````{code-block} markdown
:caption: docs/index.md

:::{card} Getting Started
:icon: rocket
:icon-style: featured

Install and configure Lumina in minutes.
:::
````

Here's the featured style:

:::{card} Getting Started
:icon: rocket
:icon-style: featured

Install and configure Lumina in minutes.
:::

Both styles work with `{grid-item-card}` too:

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

Cards without `:icon:` render exactly as before — no changes needed to existing content.

## Sidebar Icons

Give sidebar navigation items an icon by adding `icon` to a page's frontmatter:

````{code-block} yaml
:caption: docs/getting-started/index.md

---
icon: rocket
---
# Getting Started
````

The icon appears next to the page title in the sidebar. Pages without an `icon` field are unaffected — no empty space, no layout shift.

:::{tip}
Sidebar icons work best on top-level section pages. Adding icons to every nested page can create visual clutter.
:::

## Logo Icon

Use a Lucide icon as your site logo instead of a custom image. Set the `logo_icon` theme option in your `conf.py`:

```{code-block} python
:caption: conf.py

html_theme_options = {
    "logo_icon": "hexagon",
}
```

The icon renders in your accent color at the standard logo size. It works in both light and dark mode automatically.

If you also set `html_logo`, `light_logo`, or `dark_logo`, those take precedence — `logo_icon` is only used when no image logo is configured.

## Finding Icon Names

Browse the full icon set at [lucide.dev/icons](https://lucide.dev/icons/). Use the kebab-case name shown on each icon's page:

| Icon | Name |
|------|------|
| Rocket | `rocket` |
| Book Open | `book-open` |
| Circle Help | `circle-help` |
| Hexagon | `hexagon` |
| Sparkles | `sparkles` |

If you use an icon name that doesn't exist, the build continues without errors — the icon is silently omitted.
