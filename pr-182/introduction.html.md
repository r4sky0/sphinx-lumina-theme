# Introduction

## Modern documentation without leaving Sphinx

Your documentation is part of your product. Lumina helps Sphinx projects present it that way.

If Sphinx gives your project the capabilities it needs but its default presentation feels dated, Lumina gives you a clearer, more modern reading experience without asking you to migrate. Keep the Sphinx strengths you already rely on—autodoc, cross-references, versioning, MyST, and the wider extension ecosystem—while making your documentation easier and more pleasant to use.

## Why choose Lumina?

### Keep the toolchain you trust

Your existing `conf.py`, reStructuredText or MyST Markdown, and standard Sphinx extensions can stay in place. Lumina works with the standard Sphinx output model, so adopting the theme does not require a rewrite.

### Help readers find answers

Responsive navigation, clear page outlines, keyboard-friendly search, readable typography, and dark mode help readers orient themselves and stay focused, whether they are on a large monitor or a phone.

### Ship a polished site with less infrastructure

Lumina produces a static site with self-hosted fonts, client-side search, and lightweight interactivity. You get a fast, self-contained documentation site without a hosted search service or a separate frontend stack.

## Features

A responsive layout that keeps sidebar navigation, content, and page outline all visible without crowding. Collapses gracefully on smaller screens.

Light and dark themes designed together, with carefully chosen colors that maintain readability in both modes. Follows system preference by default.

Press `⌘K` / `Ctrl`+`K` to open instant full-text search powered by Pagefind. No external services, no API keys — the index ships with your docs.

Ten admonition types with distinct colors and icons, plus custom titles, nested admonitions, and collapsible dropdowns.

Syntax highlighting for 20+ languages, line numbers, line emphasis, captions, diff views, and automatic copy buttons.

Responsive card layouts, grids, tabs, badges, and buttons via sphinx-design — all styled to match the theme.

Flowcharts, sequence diagrams, class diagrams, Gantt charts, and more — with automatic dark mode support.

Inline and display equations, labeled references, multi-line systems, and matrices via MathJax.

Document REST endpoints from OpenAPI specs or hand-written directives. Every endpoint gets a **Copy as curl** button and a collapsible **Try it out** panel — no Swagger UI required.

Let readers switch between documentation versions with a dropdown loaded from a JSON file you host alongside your docs.

Source Sans 3 and JetBrains Mono are bundled with the theme. No external CDN requests, no privacy concerns.

Optional per-page reading-time estimate, computed from prose word count and ignoring code blocks. Per-page overrides via MyST front matter.

## Built with

Lumina is built on a modern but pragmatic stack:

- **Tailwind CSS v4** for utility-first styling with CSS custom properties
- **Alpine.js** for lightweight interactivity without a heavy framework
- **Pagefind** for static, client-side full-text search
- **Self-hosted fonts** (Source Sans 3, JetBrains Mono) — no external CDN calls

The theme extends Sphinx’s built-in `basic` theme, so it inherits all of Sphinx’s template machinery while replacing the visual layer entirely.

## Getting started

Ready to try it? Head to the [Getting Started](getting-started/index.md) guide to install Lumina and configure it for your project.
