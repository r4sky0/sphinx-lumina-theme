# Development Workflow

Set up live-reloading for a fast edit-preview cycle while writing documentation.

## Live Reload with sphinx-autobuild

Install `sphinx-autobuild` and run it to watch your `docs/` directory for changes:

::::{tab-set}

:::{tab-item} uv (recommended)
```bash
uv add sphinx-autobuild --dev
uv run sphinx-autobuild docs docs/_build/html --open-browser
```
:::

:::{tab-item} pip
```bash
pip install sphinx-autobuild
sphinx-autobuild docs docs/_build/html --open-browser
```
:::

::::

This watches your `docs/` directory and automatically rebuilds when files change. Your browser refreshes automatically.

:::{note}
**Search during development:** Pagefind indexes your content during full builds. During live preview with `sphinx-autobuild`, search may not be available. Use {kbd}`⌘F` / {kbd}`Ctrl+F` for in-page search instead.
:::

## Asset Watcher

:::{tip}
If you're also editing theme CSS or JavaScript source files, run the asset watcher in a separate terminal:

```bash
pnpm run dev
```

This recompiles the theme's CSS and JavaScript on every change.
:::
