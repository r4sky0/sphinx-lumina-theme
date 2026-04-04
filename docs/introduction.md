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
A responsive layout that keeps sidebar navigation, content, and page outline all visible without crowding. Collapses gracefully on smaller screens.
:::

:::{grid-item-card} Dark Mode
Light and dark themes designed together, with carefully chosen colors that maintain readability in both modes. Follows system preference by default.
:::

:::{grid-item-card} Fast Search
Press {kbd}`⌘K` / {kbd}`Ctrl+K` to open instant full-text search powered by Pagefind. No external services, no API keys — the index ships with your docs.
:::

:::{grid-item-card} Styled Admonitions
Ten admonition types with distinct colors and icons, plus custom titles, nested admonitions, and collapsible dropdowns.
:::

:::{grid-item-card} Code Blocks
Syntax highlighting for 20+ languages, line numbers, line emphasis, captions, diff views, and automatic copy buttons.
:::

:::{grid-item-card} Cards & Grids
Responsive card layouts, grids, tabs, badges, and buttons via sphinx-design — all styled to match the theme.
:::

:::{grid-item-card} Mermaid Diagrams
Flowcharts, sequence diagrams, class diagrams, Gantt charts, and more — with automatic dark mode support.
:::

:::{grid-item-card} LaTeX Math
Inline and display equations, labeled references, multi-line systems, and matrices via MathJax.
:::

:::{grid-item-card} Self-Hosted Fonts
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
