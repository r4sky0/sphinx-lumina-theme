# Read the Docs

[Read the Docs](https://about.readthedocs.com/) builds your documentation on every push and hosts each branch and tag as its own version. Lumina detects Read the Docs builds and integrates with its [addons](https://docs.readthedocs.com/platform/stable/addons.html) without extra configuration.

To see the result, browse [Lumina's own docs on Read the Docs](https://sphinx-lumina-theme.readthedocs.io/).

## Prerequisites

- A Sphinx project that builds locally with `html_theme = "lumina"`. See {doc}`/getting-started/installation`.
- The project in a Git repository on GitHub, GitLab, or Bitbucket.
- A free account on [Read the Docs](https://app.readthedocs.org/accounts/signup/).

## Step 1: Declare your docs dependencies

Read the Docs installs only what you list. Choose the tab that matches how your project manages dependencies.

::::{tab-set}

:::{tab-item} uv (recommended)
Add the docs tools to a dependency group:

```bash
uv add --group docs sphinx sphinx-lumina-theme myst-parser
```

This updates `pyproject.toml` and `uv.lock`. Commit both files.
:::

:::{tab-item} pip
Create a requirements file next to `conf.py`:

```{code-block} text
:caption: docs/requirements.txt
sphinx
sphinx-lumina-theme
myst-parser
```
:::

::::

Add any other Sphinx extensions your `conf.py` loads, such as `sphinx-design` or `sphinxcontrib-mermaid`. For Pagefind search, use `sphinx-lumina-theme[pagefind]` instead.

## Step 2: Add `.readthedocs.yaml`

Create `.readthedocs.yaml` in the repository root:

::::{tab-set}

:::{tab-item} uv (recommended)
```{code-block} yaml
:caption: .readthedocs.yaml
version: 2

build:
  os: ubuntu-24.04
  tools:
    python: "3.13"

sphinx:
  configuration: docs/conf.py

python:
  install:
    - method: uv
      command: sync
      groups:
        - docs
```
:::

:::{tab-item} pip
```{code-block} yaml
:caption: .readthedocs.yaml
version: 2

build:
  os: ubuntu-24.04
  tools:
    python: "3.13"

sphinx:
  configuration: docs/conf.py

python:
  install:
    - requirements: docs/requirements.txt
```
:::

::::

Change `docs/conf.py` if your configuration lives elsewhere. Commit the file and push.

````{tip}
If you use `sphinx-last-updated-by-git`, Read the Docs' shallow clone gives every page the same date. Fetch the full history before the build:

```yaml
build:
  jobs:
    post_checkout:
      - git fetch --unshallow || true
```
````

## Step 3: Import the project

1. Sign in to [Read the Docs](https://app.readthedocs.org/) and import your repository from the dashboard. If it isn't listed, enter its URL manually.
2. Confirm the project name. It becomes your subdomain, such as `my-project.readthedocs.io`.
3. Wait for the first build, which starts automatically and takes a minute or two.
4. Select **View docs** when the build finishes.

Read the Docs' [tutorial](https://docs.readthedocs.com/platform/stable/tutorial/index.html) walks through the import screens in detail.

## Step 4: Preview pull requests

Read the Docs builds every pull request and links the preview from the pull request's checks. This is on by default for new projects; you can change it under **Settings → Pull request builds**.

## What Lumina handles automatically

You don't need to change `conf.py` for any of these.

Canonical URL
: When `html_baseurl` is unset, Lumina uses the `READTHEDOCS_CANONICAL_URL` that Read the Docs provides. This enables canonical links, `sitemap.xml`, and the `robots.txt` sitemap line (see {doc}`/guides/seo`). A value you set in `conf.py` always takes priority.

Version switcher
: The header shows Lumina's version dropdown, filled with your project's active versions. Choosing a version opens the same page in that version. To use your own list instead, set `version_switcher_json` (see {doc}`/getting-started/configuration`).

Addon styling
: The Read the Docs flyout and version notifications use Lumina's colors and font in light and dark mode. The back-to-top button moves up so the flyout doesn't cover it.

Search
: The search box, {kbd}`/`, and {kbd}`⌘K` or {kbd}`Ctrl+K` open Lumina's search. See {doc}`/guides/search`.

To publish more versions, open **Versions** in your project dashboard and activate the branches or tags you want. They appear in the version dropdown after their first build.

## Flyout menu

Read the Docs also shows its own flyout menu in the bottom corner. Because Lumina's header already has a version switcher, you can turn the flyout off under **Settings → Addons → Flyout menu**.

Keep the flyout if readers need its extras, such as switching between translations or downloading PDF and ePub builds.

## Troubleshooting

### The build fails with "no theme named 'lumina' found"

**Cause:** `sphinx-lumina-theme` isn't in the dependencies Read the Docs installs.

**Solution:** Add it to your `docs` group or `docs/requirements.txt` (Step 1), and check that `.readthedocs.yaml` points at that file or group.

### "Extension error: Could not import extension …"

**Cause:** `conf.py` loads an extension that isn't installed in the build.

**Solution:** Add the extension's package to your docs dependencies. The build log lists the missing module name.

### The version dropdown doesn't appear

**Cause:** The dropdown appears only on Read the Docs builds and when addons are enabled. It also doesn't appear when you build locally.

**Solution:** Check that your project uses addons under **Settings → Addons**. To show a dropdown everywhere, provide your own list with `version_switcher_json`.
