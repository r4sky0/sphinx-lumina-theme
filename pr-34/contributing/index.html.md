# Contributing

How to set up a development environment and contribute to the Sphinx Lumina Theme.

## Prerequisites

You need the following tools installed:

- **Python 3.12+** and [uv](https://docs.astral.sh/uv/) for Python dependency management
- **Node.js 18+** and [pnpm](https://pnpm.io/) for JavaScript dependency management

## Development Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/r4sky0/sphinx-lumina-theme.git
cd sphinx-lumina-theme
pnpm install        # JS dependencies
uv sync --dev       # Python dependencies
```

Build the theme’s CSS and JavaScript:

```bash
pnpm run build
```

Build the documentation (which dogfoods the theme):

```bash
uv run sphinx-build docs docs/_build/html
```

Open `docs/_build/html/index.html` to see the result.

## Running Tests

```bash
uv run pytest                       # All tests
uv run pytest tests/test_build.py   # Single file
uv run pytest -k test_name          # Single test by name
```

Tests use pytest with BeautifulSoup for HTML assertions. The `build_output` fixture builds `tests/sample_docs/` with Sphinx and verifies the rendered HTML structure.

## Making Changes

1. Create a branch from `main`
2. Edit source files — see [Architecture](architecture.md) for where things live
3. If you changed CSS or JS in `_static_src/`, run `pnpm run build`
4. Build docs to verify: `uv run sphinx-build docs docs/_build/html`
5. Run tests: `uv run pytest`
6. Commit with a descriptive message

## Pull Requests

- Keep PRs focused on a single change
- Include a clear description of what changed and why
- Ensure all tests pass before requesting review

Learn how the theme is structured — build pipeline, templates, Alpine.js components, and testing.
