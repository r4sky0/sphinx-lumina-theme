# Icons

Make your docs easier to scan by adding icons to cards, sidebar navigation, and your site logo. Lumina includes all 1900+ [Lucide](https://lucide.dev/icons/) icons — rendered as inline SVG at build time with zero runtime cost.

## Card Icons

Add an `:icon:` option to any `{card}` or `{grid-item-card}` directive:

```markdown
:::{card} Getting Started
:icon: rocket

Install and configure Lumina in minutes.
:::
```

**Result:**

Install and configure Lumina in minutes.

### Featured Style

For landing pages or feature showcases, the **featured** style places a larger icon in a tinted pill above the title:

```markdown
:::{card} Getting Started
:icon: rocket
:icon-style: featured

Install and configure Lumina in minutes.
:::
```

**Result:**

Install and configure Lumina in minutes.

### Grid Cards

Both styles work with `{grid-item-card}`:

Step-by-step tutorials.

API documentation.

Common questions.

### Options Reference

| Option         | Values               | Default   | Description                                                                                           |
|----------------|----------------------|-----------|-------------------------------------------------------------------------------------------------------|
| `:icon:`       | Any Lucide icon name | —         | Icon to display on the card                                                                           |
| `:icon-style:` | `inline`, `featured` | `inline`  | `inline` places the icon next to the title. `featured` shows a larger icon in a tinted pill above it. |

Cards without `:icon:` render exactly as before.

## Sidebar Icons

Add an `icon` field to a page’s frontmatter to display it in the sidebar:

```yaml
---
icon: rocket
---
# Getting Started
```

The icon appears next to the page title in the sidebar. Pages without an `icon` field are unaffected — no empty space, no layout shift.

## Logo Icon

Use a Lucide icon as your site logo instead of a custom image:

```python
html_theme_options = {
    "logo_icon": "hexagon",
}
```

The icon renders in your accent color and adapts to both light and dark mode automatically.

`logo_icon` is only used when no image logo is configured. If you set `html_logo`, `light_logo`, or `dark_logo`, those take precedence.

## Finding Icon Names

Use the [Icon Browser](../reference/icons.md) to search all 1900+ icons and click to copy names.

Icon names use **kebab-case** — the same format shown on [lucide.dev/icons](https://lucide.dev/icons/):

| Example     | Name          |
|-------------|---------------|
| Rocket      | `rocket`      |
| Book Open   | `book-open`   |
| Circle Help | `circle-help` |
| Hexagon     | `hexagon`     |
| Sparkles    | `sparkles`    |

If you use an icon name that doesn’t exist, the build continues without errors — the icon is silently omitted.
