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

#### SEE ALSO
Pagefind only indexes during full builds, so `⌘K` search may not be populated during live preview. See [Search](search.md) for details and fallbacks.

## Asset Watcher

If you’re editing Lumina’s own CSS or JavaScript source (not just using the theme), run the asset watcher in a separate terminal:

```bash
pnpm run dev
```

This recompiles the theme’s CSS and JavaScript on every change. You don’t need this if you’re only editing your project’s documentation content.
