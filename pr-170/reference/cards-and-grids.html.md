# Cards & Grids

Layout components from sphinx-design for visually organizing content into cards and responsive grids. Requires the `sphinx_design` extension — see [sphinx-design](../extensions/sphinx-design.md) for setup.

## Basic Cards

A card with a title and body content.

Install the theme and configure your Sphinx project in under a minute.

Customize colors, navigation depth, search backend, and more through `html_theme_options`.

The MyST syntax:

```markdown
:::{card} Card Title
Card body content here.
:::
```

## Cards with Headers and Footers

Add structured sections to cards using `^^^` (header separator) and `+++` (footer separator).

Header content above the separator

The Lumina theme includes dark mode, Pagefind search, a three-column layout, and styled admonitions.

Footer — [View on GitHub](https://github.com)

The MyST syntax:

```markdown
:::{card} Title
Header content
^^^
Body content
+++
Footer content
:::
```

## Link Cards

Make entire cards clickable by adding a `:link:` option.

Step-by-step instructions for installing and configuring the Lumina theme.

The MyST syntax:

```markdown
:::{card} Clickable Card
:link: target-page
:link-type: doc
Card body.
:::
```

## Card Grids

Arrange cards in a responsive grid layout.

Headings, inline formatting, block quotes, definition lists, and more.

Note, tip, warning, danger, and 6 more callout types with custom styling.

Syntax highlighting, line numbers, emphasis, captions, and diff views.

Ordered, unordered, and task lists. Markdown and list-table formats.

Responsive images with captions, alignment, and sizing options.

Inline and display equations powered by MathJax.

The MyST syntax:

```markdown
::::{grid} 1 1 2 3
:::{grid-item-card} Title
Content
:::
::::
```

The four numbers in `1 1 2 3` set columns per breakpoint:

| Position   | Breakpoint   | Typical use                 |
|------------|--------------|-----------------------------|
| 1st        | xs (< 576px) | Phones — usually `1` column |
| 2nd        | sm (576px+)  | Large phones — `1` or `2`   |
| 3rd        | md (768px+)  | Tablets — `2` or `3`        |
| 4th        | lg (992px+)  | Desktops — `2`, `3`, or `4` |

### Gutter Spacing

Control the gap between grid items with `:gutter:`:

```markdown
::::{grid} 1 1 2 3
:gutter: 3
```

Values range from `0` (no gap) to `5` (largest gap). Default is `3`.

## Grid Layouts

Use `grid` and `grid-item` for custom layouts without the card styling.

**Left column** — This is a two-column grid without card borders. Useful for side-by-side content layouts.

**Right column** — Each grid item takes equal width by default. Adjust with `:columns:` on individual items.

## Grid Items with Custom Spans

Control how many columns each item occupies.

Narrow

This item spans 3 of 4 columns, useful for a main content area with a narrow sidebar.

The MyST syntax:

```markdown
::::{grid} 4
:::{grid-item}
:columns: 1
Sidebar
:::
:::{grid-item}
:columns: 3
Main content
:::
::::
```

## Common Patterns

### Feature overview grid

Use card grids on landing or overview pages to let readers scan features at a glance:

```markdown
::::{grid} 1 1 2 3
:gutter: 3
:::{grid-item-card} Feature Name
Brief description of what this feature does.
:::
::::
```

### Navigation cards

Make cards clickable with `:link:` to create a visual navigation menu:

```markdown
:::{card} Getting Started
:link: getting-started
:link-type: doc
Install and configure the theme.
:::
```

### Side-by-side comparison

Use a plain 2-column grid for before/after or comparison layouts:

```markdown
::::{grid} 2
:::{grid-item}
**Before**: description of the old state.
:::
:::{grid-item}
**After**: description of the new state.
:::
::::
```
