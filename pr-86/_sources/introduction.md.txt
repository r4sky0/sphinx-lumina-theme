# Introduction

## A fresh look for Sphinx

Sphinx is one of the most powerful documentation generators in the Python ecosystem. It handles cross-referencing, API docs, versioning, and internationalization better than almost anything else. But for years, many of its themes have felt stuck in another era — cramped layouts, dated typography, and little attention to the reading experience.

**Lumina changes that.**

Sphinx Lumina Theme brings the polish and clarity of modern documentation sites — think Fumadocs, Nextra, and Docusaurus — to Sphinx, without asking you to leave the ecosystem you already know.

## Why another theme?

There's no shortage of documentation tools. But most modern ones require you to abandon Sphinx entirely and rewrite your docs in a new system. That's a significant cost, especially for projects that rely on Sphinx features like autodoc, intersphinx, or domain-specific directives.

Lumina takes a different approach: **keep Sphinx, upgrade the experience.** Your existing `conf.py`, your reStructuredText or MyST Markdown, your extensions — they all work. You just get a better-looking result.

## Features

::::{grid} 1 1 2 3
:gutter: 3

:::{grid-item-card} Three-Column Layout
:icon: columns-3
:icon-style: featured
A responsive layout that keeps sidebar navigation, content, and page outline all visible without crowding. Collapses gracefully on smaller screens.
:::

:::{grid-item-card} Dark Mode
:icon: moon
:icon-style: featured
Light and dark themes designed together, with carefully chosen colors that maintain readability in both modes. Follows system preference by default.
:::

:::{grid-item-card} Fast Search
:icon: search
:icon-style: featured
Press {kbd}`⌘K` / {kbd}`Ctrl+K` to open instant full-text search powered by Pagefind. No external services, no API keys — the index ships with your docs.
:::

:::{grid-item-card} Styled Admonitions
:icon: message-square-warning
:icon-style: featured
Ten admonition types with distinct colors and icons, plus custom titles, nested admonitions, and collapsible dropdowns.
:::

:::{grid-item-card} Code Blocks
:icon: code
:icon-style: featured
Syntax highlighting for 20+ languages, line numbers, line emphasis, captions, diff views, and automatic copy buttons.
:::

:::{grid-item-card} Cards & Grids
:icon: layout-grid
:icon-style: featured
Responsive card layouts, grids, tabs, badges, and buttons via sphinx-design — all styled to match the theme.
:::

:::{grid-item-card} Mermaid Diagrams
:icon: git-branch
:icon-style: featured
Flowcharts, sequence diagrams, class diagrams, Gantt charts, and more — with automatic dark mode support.
:::

:::{grid-item-card} LaTeX Math
:icon: sigma
:icon-style: featured
Inline and display equations, labeled references, multi-line systems, and matrices via MathJax.
:::

:::{grid-item-card} Interactive HTTP API
:icon: server
:icon-style: featured
Document REST endpoints from OpenAPI specs or hand-written directives. Every endpoint gets a **Copy as curl** button and a collapsible **Try it out** panel — no Swagger UI required.
:::

:::{grid-item-card} Version Switcher
:icon: git-compare
:icon-style: featured
Let readers switch between documentation versions with a dropdown loaded from a JSON file you host alongside your docs.
:::

:::{grid-item-card} Self-Hosted Fonts
:icon: type
:icon-style: featured
Source Sans 3 and JetBrains Mono are bundled with the theme. No external CDN requests, no privacy concerns.
:::

::::

## Built with

Lumina is built on a modern but pragmatic stack:

- **Tailwind CSS v4** for utility-first styling with CSS custom properties
- **Alpine.js** for lightweight interactivity without a heavy framework
- **Pagefind** for static, client-side full-text search
- **Self-hosted fonts** (Source Sans 3, JetBrains Mono) — no external CDN calls

The theme extends Sphinx's built-in `basic` theme, so it inherits all of Sphinx's template machinery while replacing the visual layer entirely.

## Getting started

Ready to try it? Head to the {doc}`getting-started/index` guide to install Lumina and configure it for your project.

:::{tip}
Try dark mode now — click the sun/moon button in the header. Your preference persists across sessions, and the docs you're reading are built with Lumina themselves.
:::
