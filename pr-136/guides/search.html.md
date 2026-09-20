# Search

Configure how readers search your documentation — Pagefind for fast client-side search, or Sphinx’s built-in search as a fallback.

## Pagefind (default)

[Pagefind](https://pagefind.app) provides fast, keyboard-driven search with no external services. Press `⌘K` or `Ctrl`+`K` to open the search modal.

Lumina runs Pagefind automatically at the end of each build. Install the pinned CLI in your documentation project:

```bash
pnpm add -D pagefind@1.3.0
```

Theme contributors can use `pnpm install` to install the repository’s locked version. You can also expose a Pagefind executable on `PATH`.

Build your docs and search is ready:

### uv (recommended)

```bash
uv run sphinx-build docs docs/_build/html
```

### pip

```bash
sphinx-build docs docs/_build/html
```

## Built-in Sphinx Search

If you prefer not to use Pagefind, switch to Sphinx’s built-in search:

```python
html_theme_options = {
    "search_backend": "sphinx",
}
```

The built-in search works without any additional setup but is slower and less featured than Pagefind.

#### NOTE
**Search during development:** Pagefind indexes your content during full builds. During live preview with `sphinx-autobuild`, search may not be available. Use `⌘F` / `Ctrl`+`F` for in-page search instead.
