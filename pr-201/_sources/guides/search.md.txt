# Search

Configure how readers search your documentation: Sphinx's built-in search by default, or Pagefind for fast client-side search with section filters and heading results.

## Pagefind

[Pagefind](https://pagefind.app) provides fast, keyboard-driven search with no external services. Press {kbd}`⌘K` or {kbd}`Ctrl+K` to open the search modal.

Pagefind is opt-in. Install the theme with the `pagefind` extra, which pins a tested Pagefind release:

::::{tab-set}

:::{tab-item} uv (recommended)
```bash
uv add "sphinx-lumina-theme[pagefind]"
```
:::

:::{tab-item} pip
```bash
pip install "sphinx-lumina-theme[pagefind]"
```
:::

::::

Then enable it in `conf.py`:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "search_backend": "pagefind",
}
```

Lumina runs Pagefind at the end of each build, so search is ready as soon as the build finishes. No Node.js is required.

:::{tip}
If the `pagefind` extra is not installed, the build completes normally with a warning but search won't be indexed.
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

## API symbols

Functions, classes and other objects documented with Sphinx domains, such as
`py:function` or a third-party API domain, are matched by name and listed above
the page results, up to five at a time. Type a member name such as `connect` or a
qualified name such as `EventEmitter.on`, then select a result to jump to its
definition. Symbols follow the rules of Sphinx's own search: objects with a
negative search priority and pages marked `:nosearch:` are left out. Lumina writes
them to `_static/lumina-symbols.json` at the end of each build, for both search
backends.

## Built-in Sphinx Search

Sphinx's built-in search is the default and needs no extra tools. To switch back from Pagefind, remove `search_backend` or set it explicitly:

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
