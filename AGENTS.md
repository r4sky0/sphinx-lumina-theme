# Repository Guidelines

## Project Overview

Lumina is a modern Sphinx documentation theme built with Tailwind CSS v4 and Alpine.js. It is registered as the `lumina` theme through the `sphinx.html_themes` entry point.

## Project Structure & Module Organization

`src/sphinx_lumina_theme/` contains the Python package and Sphinx theme. Edit CSS and JavaScript in `_static_src/css/` and `_static_src/js/`; `scripts/build-assets.js` compiles them into `theme/static/`. Jinja templates live in `theme/`, with reusable pieces in `theme/components/`. Documentation and the live theme showcase are in `docs/` (MyST Markdown). Tests live in `tests/`, with Sphinx fixtures in `tests/sample_docs/`. See `docs/contributing/architecture.md` for the build pipeline.

```text
src/sphinx_lumina_theme/
├── __init__.py              # Sphinx setup() hook, registers the theme
├── _static_src/             # Source assets; edit these
│   ├── css/                 # base.css imports admonitions, code, and typography
│   └── js/                  # app.js is the entry point and loads Alpine components
└── theme/                   # Sphinx theme
    ├── layout.html          # Master template, extends basic/layout.html
    ├── theme.toml           # Theme configuration and options
    ├── components/          # Jinja2 partials
    └── static/              # Compiled CSS/JS and fonts; do not edit directly
```

## Build, Test, and Development Commands

- `pnpm install` and `uv sync --dev`: install JavaScript and Python development dependencies.
- `pnpm run build`: compile production CSS and JavaScript after changing `_static_src/`.
- `pnpm run dev`: watch theme assets during development.
- `uv run sphinx-build docs docs/_build/html -W`: build the documentation and treat warnings as errors.
- `uv run pytest`: run all tests; use `uv run pytest tests/test_build.py` for a focused run.
- `uv run ruff check .`, `uv run ruff format --check .`, and `uv run djlint src/sphinx_lumina_theme/theme/ --check`: run CI style checks.

The asset build uses esbuild to bundle `_static_src/js/app.js` into `theme/static/lumina.js` as an IIFE and Tailwind CLI to process `_static_src/css/base.css` into `theme/static/lumina.css`. Tailwind scans the templates and JavaScript files for class usage. Run `pnpm run build` after changing CSS or JavaScript source files because Sphinx serves the compiled files.

## Using uv

Run `uv` commands from the repository root. `uv sync --dev` creates or updates this repository's `.venv` from `pyproject.toml` and `uv.lock`; after that, prefer `uv run ...` so the command uses the locked project environment:

```bash
uv sync --dev
uv run pytest
uv run python scripts/record-demo.py
uv run sphinx-build docs docs/_build/html -W
```

Use `uv add package-name` for runtime dependencies and `uv add --dev package-name` for development dependencies. These commands update `pyproject.toml` and `uv.lock`; do not edit the lockfile by hand.

Do not copy `PATH`, `PYTHONPATH`, or `.venv/bin/python` paths from another checkout or temporary directory. In particular, `UV_NO_SYNC=1` skips environment synchronization and is only appropriate when the current checkout's environment is already prepared intentionally. The usual local command is simply `uv run pytest`.

The repository uses pnpm for JavaScript and uv for Python; do not use npm or pip.

## Theme Behavior

Alpine.js components are registered with `Alpine.data()` in modules under `_static_src/js/`. Components are imported and registered in `app.js`, then referenced in templates with `x-data`.

When creating elements with `document.createElement()` and setting Alpine directives through `setAttribute()`, use long-form attributes such as `x-on:click` and `x-bind:class`. WebKit/Safari rejects shorthand `@click` and `:class` in `setAttribute()`; shorthand remains valid in HTML templates parsed by the browser.

Dark mode uses CSS custom properties such as `--lumina-accent`, `--lumina-bg`, and `--lumina-text`, toggled by `[data-theme="dark"]` on `<html>`. The preference is stored under `lumina-theme`, and the inline `extrahead` script in `layout.html` applies it before paint to prevent FOUC.

## Coding Style & Naming Conventions

Use four spaces in Python and Jinja templates; `djlint` is configured with a 120-character limit for templates. Follow the existing two-space JavaScript style. Name Python modules and functions with `snake_case`; use descriptive hyphenated names for JavaScript, CSS, and template files. Edit source assets rather than compiled files in `theme/static/`. Ruff formats and checks Python; djlint formats Jinja. The pre-commit hook runs these tools on staged files.

Use self-hosted fonts only (Source Sans 3 and JetBrains Mono). Keep Sphinx template inheritance through the `basic` theme and override blocks instead of replacing the inheritance chain. See `.impeccable.md` for brand guidelines, design philosophy, and reference sites.

## Testing Guidelines

Write pytest tests as `tests/test_*.py` with `test_*` functions. Structural tests build `tests/sample_docs/` and inspect rendered HTML with BeautifulSoup; the session-scoped `build_output` fixture builds the sample docs and returns the output path. Tests verify rendered HTML structure rather than visual appearance. Browser behavior is covered in `tests/test_browser.py` with Playwright. Add or update focused tests when behavior changes. Run the full suite and a docs build before submitting a PR; browser tests need installed Playwright browsers. No coverage threshold is configured.

## Documentation

Docs use MyST Markdown, and the theme dogfoods itself through `conf.py` with `html_theme = "lumina"`. Supported extensions include `myst_parser`, `sphinx_design`, and `sphinx_copybutton`.

The docs use a hub-and-spoke structure with `getting-started/`, `guides/`, `extensions/`, `reference/`, and `contributing/` sections. Each section has an `index.md` hub with card grids; the root `docs/index.md` toctree references the section hubs.

When a change affects user-facing behavior, update the relevant documentation:

- Theme options: `docs/getting-started/configuration.md` and the relevant guide.
- CSS custom properties: `docs/guides/custom-styling.md`.
- Extensions: add or update the page under `docs/extensions/`.
- New reference content: add it under `docs/reference/` and link it from `docs/reference/index.md`.
- Templates or components: `docs/contributing/architecture.md`.
- Cross-references: use absolute `{doc}` links such as `/extensions/mermaid`.

When adding a page, include it in the parent section's `index.md` toctree and card grid.

## Workflow Notes

`git rebase --continue` does not trigger the pre-commit hook. After resolving rebase conflicts, verify HTML templates manually with:

```bash
uv run djlint src/sphinx_lumina_theme/theme/ --check
```

## Commit & Pull Request Guidelines

Use Conventional Commits, as enforced by commitlint: `feat: add navigation option`, `fix(search): handle empty query`, or `docs: clarify setup`. Keep pull requests focused. Fill in the PR template's summary and test plan, link related issues when applicable, and include before/after screenshots or a recording for visual changes. Verify the affected feature in light and dark mode.
