# Wide Layout

Lumina limits the center column to 50rem, including its padding. Paragraphs, lists, code blocks, and other content share that column's full usable width. Wide mode expands the column to 60rem for code-heavy documentation and wide tables.

On large screens, the navigation background extends to the left edge of the viewport. Navigation links and the page outline stay close to the article.

## Reader Toggle

Let readers choose between normal and wide layouts with a toggle button in the header:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "wide_layout": "toggle",
}
```

This adds a toggle button next to the dark mode switch. The toggle is only visible on screens 1280px and wider, since narrower viewports don't have extra space to use. The reader's preference is persisted in `localStorage`.

## Always Wide

Force wide mode permanently — no toggle, always wide:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "wide_layout": "always",
}
```

This is useful when your entire documentation is code-heavy and you want every reader to see the wider layout without having to discover and click a toggle.

## How It Works

When a reader clicks the toggle, Lumina sets the `data-layout` attribute on the `<html>` element:

- **Normal layout:** no `data-layout` attribute (content max-width: 50rem)
- **Wide layout:** `<html data-layout="wide">` (content max-width: 60rem)

The reader's choice is persisted in `localStorage` under the key `lumina-layout`. An inline script applies the layout before the first paint, preventing layout shift on page load.

## What Changes in Wide Mode

| Element | Normal | Wide |
|---------|--------|------|
| Page wrapper | 80rem (1280px) | 90rem (1440px) |
| Content area, including padding | 50rem (800px) | 60rem (960px) |
| Header | 80rem | 90rem |
| Sidebars | Unchanged | Unchanged |

The left navigation sidebar (260px) and right table of contents (220px) stay the same width. All extra space goes to the content column.

Paragraphs wrap at spaces by default. For automatic word separation at syllable boundaries, see the hyphenation example in {doc}`/guides/custom-styling`.

## Customizing Wide Mode Widths

You can override the wide mode widths in a custom stylesheet:

```{code-block} python
:caption: conf.py
html_static_path = ["_static"]
html_css_files = ["custom.css"]
```

```{code-block} css
:caption: docs/_static/custom.css
[data-layout="wide"] .lumina-wrapper {
    max-width: 110rem;
}

[data-layout="wide"] #lumina-content {
    max-width: 70rem;
}
```

:::{tip}
Wide layout pairs well with code-heavy documentation. For prose-focused sites, the default width provides a better reading experience.
:::
