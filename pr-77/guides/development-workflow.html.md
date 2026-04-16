# Development Workflow

Set up live-reloading for a fast edit-preview cycle while writing documentation.

## Live Reload with sphinx-autobuild

Install `sphinx-autobuild` and run it to watch your `docs/` directory for changes:

### uv (recommended)

```bash
uv add sphinx-autobuild --dev
uv run sphinx-autobuild docs docs/_build/html --open-browser
```

### pip

```bash
pip install sphinx-autobuild
sphinx-autobuild docs docs/_build/html --open-browser
```

This watches your `docs/` directory and automatically rebuilds when files change. Your browser refreshes automatically.

#### NOTE
**Search during development:** Pagefind indexes your content during full builds. During live preview with `sphinx-autobuild`, search may not be available. Use `⌘F` / `Ctrl`+`F` for in-page search instead.

## Asset Watcher
