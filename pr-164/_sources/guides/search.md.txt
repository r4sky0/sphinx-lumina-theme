# Search

Configure how readers search your documentation — Pagefind for fast client-side search, or Sphinx's built-in search as a fallback.

## Pagefind (default)

[Pagefind](https://pagefind.app) provides fast, keyboard-driven search with no external services. Press {kbd}`⌘K` or {kbd}`Ctrl+K` to open the search modal.

Lumina runs Pagefind automatically at the end of each build — no manual setup required. You just need [Node.js](https://nodejs.org) installed so that `npx` is available.

Build your docs and search is ready:

::::{tab-set}

:::{tab-item} uv (recommended)
```bash
uv run sphinx-build docs docs/_build/html
```
:::

:::{tab-item} pip
```bash
sphinx-build docs docs/_build/html
```
:::

::::

:::{tip}
If `npx` is not found, the build completes normally but search won't be indexed. Install Node.js to enable Pagefind, or switch to Sphinx's built-in search below.
:::

## Search within a section

Use **Search in** below the search field to narrow results to one section, or
choose **All docs** to search the whole documentation build. Opening the dialog
starts with **All docs** each time. When a section has no matches, **Search all
docs** broadens the search without changing your query.

Scopes come from your {doc}`doc sections </guides/navigation>` configuration,
including multi-path and default sections. Without `doc_sections`, Lumina uses
the root toctree's document titles and includes each entry's descendants. A page
listed under several branches belongs to the first one. Pages outside those
branches remain available through **All docs**. The selector appears only when
at least two sections are indexed; no tags or additional options are required.

Results show navigation breadcrumbs and up to three matching headings beneath
each page. Select a heading to jump directly to that passage. Use the arrow keys
from the search field to move through page and heading links, then press
{kbd}`Enter` to open one. {kbd}`Tab` reaches the scope selector and result links.

Search covers the current build, not other versions or separately hosted sites.
Rebuild your docs after changing the navigation so the index reflects it.

## Built-in Sphinx Search

If you prefer not to use Pagefind, switch to Sphinx's built-in search:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "search_backend": "sphinx",
}
```

The built-in search works without any additional setup. It searches all pages
and does not provide section filters or heading results in the dialog. If
Pagefind cannot load or a query fails, Lumina offers a link to this search page.

:::{note}
**Search during development:** Pagefind indexes your content during full builds. During live preview with `sphinx-autobuild`, search may not be available. Use {kbd}`⌘F` / {kbd}`Ctrl+F` for in-page search instead.
:::
