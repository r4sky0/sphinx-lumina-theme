# Repository Guidelines

## Project Structure & Module Organization

`src/sphinx_lumina_theme/` contains the Python package and Sphinx theme. Edit CSS and JavaScript in `_static_src/css/` and `_static_src/js/`; `scripts/build-assets.js` compiles them into `theme/static/`. Jinja templates live in `theme/`, with reusable pieces in `theme/components/`. Documentation and the live theme showcase are in `docs/` (MyST Markdown). Tests live in `tests/`, with Sphinx fixtures in `tests/sample_docs/`. See `docs/contributing/architecture.md` for the build pipeline.

## Build, Test, and Development Commands

- `pnpm install` and `uv sync --dev`: install JavaScript and Python development dependencies.
- `pnpm run build`: compile production CSS and JavaScript after changing `_static_src/`.
- `pnpm run dev`: watch theme assets during development.
- `uv run sphinx-build docs docs/_build/html -W`: build the documentation and treat warnings as errors.
- `uv run pytest`: run all tests; use `uv run pytest tests/test_build.py` for a focused run.
- `uv run ruff check .`, `uv run ruff format --check .`, and `uv run djlint src/sphinx_lumina_theme/theme/ --check`: run CI style checks.

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

## Coding Style & Naming Conventions

Use four spaces in Python and Jinja templates; `djlint` is configured with a 120-character limit for templates. Follow the existing two-space JavaScript style. Name Python modules and functions with `snake_case`; use descriptive hyphenated names for JavaScript, CSS, and template files. Edit source assets rather than compiled files in `theme/static/`. Ruff formats and checks Python; djlint formats Jinja. The pre-commit hook runs these tools on staged files.

## Testing Guidelines

Write pytest tests as `tests/test_*.py` with `test_*` functions. Structural tests build `tests/sample_docs/` and inspect rendered HTML with BeautifulSoup; browser behavior is covered in `tests/test_browser.py` with Playwright. Add or update focused tests when behavior changes. Run the full suite and a docs build before submitting a PR; browser tests need installed Playwright browsers. No coverage threshold is configured.

## Commit & Pull Request Guidelines

Use Conventional Commits, as enforced by commitlint: `feat: add navigation option`, `fix(search): handle empty query`, or `docs: clarify setup`. Keep pull requests focused. Fill in the PR template's summary and test plan, link related issues when applicable, and include before/after screenshots or a recording for visual changes. Verify the affected feature in light and dark mode.
