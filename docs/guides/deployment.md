# Deployment

Ship your Lumina-built docs to the web. All four recipes below are copy-pasteable starting points — adjust paths, Python versions, and branch names to match your project.

:::{important}
Lumina runs Pagefind automatically at the end of `sphinx-build` when `npx` is available. For this to work in CI, Node.js must be installed **before** `sphinx-build` runs. Each recipe below installs both Python and Node.
:::

## GitHub Pages

Create `.github/workflows/docs.yml`:

```{code-block} yaml
:caption: .github/workflows/docs.yml
name: Docs

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install uv
        run: pipx install uv

      - name: Install dependencies
        run: uv sync

      - name: Build docs
        run: uv run sphinx-build docs docs/_build/html

      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs/_build/html

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

Then enable GitHub Pages in **Settings → Pages → Source: GitHub Actions**.

## Netlify

Create `netlify.toml` at the repo root:

```{code-block} toml
:caption: netlify.toml
[build]
  command = "pip install uv && uv sync && uv run sphinx-build docs docs/_build/html"
  publish = "docs/_build/html"

[build.environment]
  PYTHON_VERSION = "3.12"
  NODE_VERSION = "20"
```

Netlify detects the file on push and runs the build. Pagefind indexes as part of `sphinx-build`.

## Read the Docs

Create `.readthedocs.yaml` at the repo root:

```{code-block} yaml
:caption: .readthedocs.yaml
version: 2

build:
  os: ubuntu-24.04
  tools:
    python: "3.12"
    nodejs: "20"
  commands:
    - pip install uv
    - uv sync
    - uv run sphinx-build docs $READTHEDOCS_OUTPUT/html

sphinx:
  configuration: docs/conf.py
```

:::{note}
Read the Docs' standard build skips the `build.commands` block and installs its own Sphinx. The `commands` override above is required so Node (and therefore Pagefind) is available. If you'd rather use RTD's built-in search instead of Pagefind, set `search_backend = "sphinx"` in `html_theme_options` and omit the Node install.
:::

## Vercel

Create `vercel.json` at the repo root:

```{code-block} json
:caption: vercel.json
{
  "buildCommand": "pip install uv && uv sync && uv run sphinx-build docs docs/_build/html",
  "outputDirectory": "docs/_build/html",
  "framework": null
}
```

Vercel's default runtime already includes Python and Node, so no extra setup is needed.

## Verifying search after deploy

Once deployed, open your site and press {kbd}`⌘K` / {kbd}`Ctrl+K`. If you see `Search requires Pagefind indexing…`, the Pagefind step didn't run — check your CI logs for the `npx pagefind` invocation and confirm Node is installed before `sphinx-build`.
