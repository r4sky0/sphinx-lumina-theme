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

## Built-in Sphinx Search

If you prefer not to use Pagefind, switch to Sphinx's built-in search:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "search_backend": "sphinx",
}
```

The built-in search works without any additional setup but is slower and less featured than Pagefind.

:::{note}
**Search during development:** Pagefind indexes your content during full builds. During live preview with `sphinx-autobuild`, search may not be available. Use {kbd}`⌘F` / {kbd}`Ctrl+F` for in-page search instead.
:::
