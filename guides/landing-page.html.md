# Landing Page

A landing page gives your docs a distinctive entry point — full-width, no sidebar, with an optional hero section. It’s opt-in: add one line to any page’s frontmatter to activate it.

## Quick start

Add `template: landing.html` to any page’s frontmatter:

```yaml
---
template: landing.html
---

# Welcome to My Project

Your content goes here.
```

That’s it. The page renders without a sidebar or table of contents, in a wide single-column layout.

## Adding a hero section

Set `hero_title` to enable a hero section above the page body:

```yaml
---
template: landing.html
hero_title: My Project
hero_subtitle: Fast, reliable docs for your users.
hero_primary_text: Get started
hero_primary_url: getting-started/installation
hero_secondary_text: GitHub
hero_secondary_url: https://github.com/you/project
hero_tags: Open source, MIT license, Python 3.11+
---
```

The hero only renders when `hero_title` is set. All other hero fields are optional — add only the ones you need.

## Hero field reference

| Field                 | Description                                                                                                                                         |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `hero_title`          | Main heading. Required for the hero section to appear.                                                                                              |
| `hero_subtitle`       | Subheading below the title.                                                                                                                         |
| `hero_primary_text`   | Primary call-to-action button label.                                                                                                                |
| `hero_primary_url`    | Internal doc path (e.g. `getting-started/installation`). Resolved relative to the Sphinx build — use the same format as a Sphinx `:doc:` reference. |
| `hero_secondary_text` | Secondary button label.                                                                                                                             |
| `hero_secondary_url`  | URL for the secondary button. External URLs (`https://…`) open in a new tab automatically.                                                          |
| `hero_tags`           | Comma-separated tags rendered below the buttons (e.g. `Fast, Lightweight, Open source`).                                                            |

## Adding content below the hero

Any Markdown body below the frontmatter renders in a wide single-column layout under the hero. Use it for a feature overview, a getting-started callout, or whatever fits your project:

```markdown
---
template: landing.html
hero_title: My Project
hero_subtitle: Simple, powerful, open source.
hero_primary_text: Get started
hero_primary_url: getting-started/installation
---

## Why My Project?

A short paragraph explaining the value proposition.

::::{grid} 1 1 2 3
:gutter: 3

:::{grid-item-card} Fast
Processes thousands of items per second.
:::

:::{grid-item-card} Reliable
Battle-tested in production since 2022.
:::

:::{grid-item-card} Open source
MIT license. Contributions welcome.
:::

::::
```

## Behavior notes

- The sidebar, table of contents, and breadcrumbs are hidden on landing pages.
- The page body is still indexed by Pagefind.
- A landing page can be used for any page, not just the root `index.md`.
- The secondary button detects external URLs automatically — any URL containing `://` opens in a new tab with `rel="noopener"`.
