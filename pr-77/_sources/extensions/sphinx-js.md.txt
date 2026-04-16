# sphinx-js

[sphinx-js](https://github.com/mozilla/sphinx-js) auto-generates JavaScript API documentation from JSDoc comments in your source code. It runs [JSDoc](https://jsdoc.app/) under the hood and renders the output as native Sphinx content — fully styled by Lumina.

## Setup

Install both the Sphinx extension and JSDoc:

```bash
uv add --dev sphinx-js
pnpm add -D jsdoc
```

Add the extension to your Sphinx configuration:

```{code-block} python
:caption: conf.py
extensions = ["sphinx_js"]

js_source_path = "../src/js"          # path to your JS source (relative to conf.py)
jsdoc_config_path = "../jsdoc.json"   # path to your JSDoc config
```

Create a JSDoc configuration file at the project root:

```{code-block} json
:caption: jsdoc.json
{
  "source": {
    "include": ["src/js"],
    "includePattern": ".+\\.js$"
  },
  "opts": {
    "recurse": true
  }
}
```

:::{warning}
Do **not** enable JSDoc's `plugins/markdown` plugin. It converts descriptions to HTML before sphinx-js sees them, causing raw HTML tags to appear in the rendered output. sphinx-js expects plain text and handles formatting natively via reStructuredText.
:::

## Writing JSDoc Comments

Add JSDoc blocks above your exported functions. sphinx-js picks up `@function`, `@returns`, `@param`, and description text.

```javascript
/**
 * @module utils
 * @description Helper utilities for the application.
 */

/**
 * Format a date as a human-readable relative string (e.g. "3 days ago").
 *
 * @function formatRelativeDate
 * @param {Date} date - The date to format.
 * @param {string} [locale="en"] - BCP 47 locale tag.
 * @returns {string} A relative time string.
 */
export function formatRelativeDate(date, locale = "en") {
  // ...
}
```

### Documenting Properties and Methods

For factory functions that return objects (common with Alpine.js, Vue options, or similar patterns), list properties and methods in the description using RST-compatible formatting:

```javascript
/**
 * Factory for the theme toggle component.
 *
 * **Properties:**
 *
 * - ``mode`` *(string)* — Current mode: ``"auto"``, ``"light"``, or ``"dark"``.
 *
 * **Methods:**
 *
 * - ``init()`` — Reads stored preference and applies the theme.
 * - ``cycle()`` — Advances to the next mode.
 *
 * @function themeToggle
 * @returns {object} Component data object.
 */
export default function themeToggle() {
  return {
    mode: "auto",
    init() { /* ... */ },
    cycle() { /* ... */ },
  };
}
```

:::{tip}
Use double backticks (` `` `) for inline code in JSDoc descriptions — this is reStructuredText syntax, which sphinx-js renders natively. Single backticks produce hyperlink references in RST, not code formatting.
:::

## Usage in Documentation

Reference documented functions with the `js:autofunction` directive:

````markdown
```{js:autofunction} formatRelativeDate
```
````

This renders the function signature, parameters, return type, and description — all pulled from the JSDoc comment.

### Organizing Multiple Functions

Group related functions under headings on a single page:

````markdown
# JavaScript API

## Utilities

```{js:autofunction} formatRelativeDate
```

```{js:autofunction} debounce
```

## Components

```{js:autofunction} themeToggle
```
````

### Other Directives

sphinx-js provides several directives:

```{list-table}
:header-rows: 1
:widths: 35 65

* - Directive
  - Purpose
* - `js:autofunction`
  - Document a single function or method.
* - `js:autoclass`
  - Document a class with its constructor and members.
* - `js:autoattribute`
  - Document a module-level constant or variable.
* - `js:automodule`
  - Document all exports from a module at once.
```

## Example Output

This theme's own JavaScript components are documented with sphinx-js. See the {doc}`/contributing/javascript-api` page for a real-world example of all these patterns in action.

## Troubleshooting

### JSDoc can't parse ES module imports

Ensure you're using JSDoc 4.x, which supports ES module syntax (`import`/`export`). Older versions require the `jsdoc-babel` plugin.

```bash
pnpm add -D jsdoc@^4.0
```

### Functions don't appear in the output

- Verify the function has a `/** ... */` doc block (not `// ...` comments).
- Check that `js_source_path` in `conf.py` points to the directory containing your JS files.
- Run JSDoc directly to confirm it finds your functions:

  ```bash
  npx jsdoc -c jsdoc.json -X | python -m json.tool | head -50
  ```

### Escaped HTML tags in rendered docs

Remove `"plugins": ["plugins/markdown"]` from your `jsdoc.json`. This plugin converts descriptions to HTML before sphinx-js processes them. sphinx-js expects plain text with RST formatting.
