# Troubleshooting

Solutions to common issues when using Lumina.

## Search

### Search returns no results

Pagefind needs to index your built HTML. Run the indexer after every build:

```bash
uv run sphinx-build docs docs/_build/html
pagefind --site docs/_build/html
```

If you skip the second command, the search modal opens but finds nothing.

### Search modal doesn't open

Check that the `search_backend` option matches your setup:

```python
# If using Pagefind (default)
html_theme_options = {
    "search_backend": "pagefind",
}

# If NOT using Pagefind
html_theme_options = {
    "search_backend": "sphinx",
}
```

Also verify Pagefind is installed:

```bash
pagefind --version
```

### Pagefind not found

Install Pagefind globally:

```bash
npm install -g pagefind
```

Or use npx without installing:

```bash
npx pagefind --site docs/_build/html
```

## Build Issues

### Theme not found: "lumina"

The package isn't installed in your current Python environment.

```bash
# Check if it's installed
uv pip list | grep lumina

# Install it
uv add sphinx-lumina-theme@git+https://github.com/ralph089/sphinx-lumina-theme.git
```

If you're using a virtual environment, make sure it's activated before building.

### MyST directive not recognized

Enable the required MyST extension. For example, if `:::` syntax isn't working:

```python
myst_enable_extensions = [
    "colon_fence",    # Required for ::: directives
]
```

Common directives and their required extensions:

```{list-table}
:header-rows: 1
:widths: 40 30 30

* - Syntax
  - Extension
  - Package
* - `:::{note}` (colon fence)
  - `colon_fence`
  - myst-parser
* - `$math$`
  - `dollarmath`
  - myst-parser
* - `- [x] task`
  - `tasklist`
  - myst-parser
* - `:::{card}`
  - —
  - sphinx-design
* - `:::{mermaid}`
  - —
  - sphinxcontrib-mermaid
```

### Sphinx build warnings about missing references

If you see `WARNING: unknown document` for pages you've created, check that:

1. The file has the correct extension (`.md` for MyST, `.rst` for reStructuredText)
2. The file is included in a `toctree` directive
3. The file is not listed in `exclude_patterns` in `conf.py`

## Styling

### Styles look broken or missing

Lumina's compiled CSS must be present in `theme/static/`. If you installed from source and the styles are missing:

```bash
pnpm install
pnpm run build
```

If you installed via pip/uv from the git repository, the compiled assets should be included. Try reinstalling:

```bash
uv add --reinstall sphinx-lumina-theme@git+https://github.com/ralph089/sphinx-lumina-theme.git
```

### Custom CSS not loading

Verify your `conf.py` includes the static path and CSS file:

```python
html_static_path = ["_static"]
html_css_files = ["custom.css"]
```

Then confirm the file exists at `docs/_static/custom.css`.

### Accent color not applying

The `accent_color` option must be a valid CSS color string:

```python
# Correct
html_theme_options = {"accent_color": "#3b82f6"}

# Wrong — missing quotes or hash
html_theme_options = {"accent_color": "3b82f6"}
```

## Dark Mode

### Dark mode doesn't persist

Lumina stores the user's preference in `localStorage` under the key `lumina-theme`. This requires:

- The site is served over HTTP(S), not opened as a local `file://` URL
- The browser allows `localStorage` (no private mode restrictions)

For local preview, use a development server:

```bash
python -m http.server -d docs/_build/html
```

### Flash of wrong theme on page load

Lumina includes an inline script that applies the saved theme before the page paints. If you see a flash, check that you haven't moved or removed the `extrahead` block in a custom `layout.html` template.

## Mermaid Diagrams

### Diagrams not rendering

1. Confirm the extension is installed and configured:

   ```bash
   uv add sphinxcontrib-mermaid
   ```

   ```python
   extensions = ["sphinxcontrib.mermaid"]
   ```

2. Diagrams render client-side via JavaScript. They won't appear if you open the HTML file directly — use a local server.

### Diagrams don't match dark mode

Lumina automatically re-renders Mermaid diagrams when the theme toggles. If this isn't working, ensure you're using the latest version of the theme.

## Still Stuck?

If none of these solutions help, [open an issue](https://github.com/ralph089/sphinx-lumina-theme/issues) with:

- Your `conf.py` (redact any sensitive values)
- The full error output from `sphinx-build`
- Your Python and Sphinx versions (`uv run sphinx-build --version`)
