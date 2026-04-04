# Extensions

Lumina works with any Sphinx extension. This page covers the extensions we recommend and how to configure them for the best experience.

## MyST Parser

[MyST Parser](https://myst-parser.readthedocs.io/) lets you write documentation in Markdown instead of reStructuredText, with full access to Sphinx directives and roles.

### Setup

```bash
uv add myst-parser
```

```python
extensions = ["myst_parser"]

myst_enable_extensions = [
    "colon_fence",     # Use ::: for directives instead of ```
    "dollarmath",      # $inline$ and $$display$$ LaTeX math
    "amsmath",         # Multi-line equation environments
    "tasklist",        # - [x] checkbox task lists
    "deflist",         # Definition lists (Term\n: Definition)
    "fieldlist",       # :Key: Value metadata lists
    "substitution",    # {{variable}} template replacements
]
```

### Substitutions

Define reusable variables in `conf.py`:

```python
myst_substitutions = {
    "project_name": "My Project",
    "version": "1.0.0",
}
```

Use them in any `.md` file:

```markdown
Welcome to {{project_name}} version {{version}}.
```

### Colon Fence Syntax

The `colon_fence` extension gives you a cleaner syntax for directives:

**Colon fence** (recommended):

```markdown
:::{note}
This is cleaner and easier to type.
:::
```

**Backtick fence** (standard):

```markdown
```{note}
This also works, but nesting gets awkward.
```
```

The colon syntax is especially helpful for nested directives — just add more colons for each level.

## sphinx-design

[sphinx-design](https://sphinx-design.readthedocs.io/) adds cards, grids, tabs, badges, buttons, and dropdowns. Lumina styles all of these components with its own design language.

### Setup

```bash
uv add sphinx-design
```

```python
extensions = ["sphinx_design"]
```

### What You Get

Contained content blocks with optional headers, footers, and links.

See [Cards & Grids](reference/cards-and-grids.md)

Responsive layouts with configurable columns per breakpoint.

See [Cards & Grids](reference/cards-and-grids.md)

Tabbed content panels for grouping related information.

See [Code Blocks](reference/code-blocks.md)

Inline status labels with color variants.

See [Badges & Buttons](reference/badges-and-buttons.md)

Styled link buttons with primary and secondary variants.

See [Badges & Buttons](reference/badges-and-buttons.md)

Collapsible content sections.

See [Admonitions](reference/admonitions.md)

## sphinx-copybutton

[sphinx-copybutton](https://sphinx-copybutton.readthedocs.io/) adds a copy-to-clipboard button to every code block. Lumina positions and styles it automatically.

### Setup

```bash
uv add sphinx-copybutton
```

```python
extensions = ["sphinx_copybutton"]
```

No additional configuration needed. The button appears on hover in the top-right corner of any code block.

### Filtering Prompt Characters

If your code blocks include shell prompts, configure the extension to strip them when copying:

```python
copybutton_prompt_text = r">>> |\.\.\. |\$ |> "
copybutton_prompt_is_regexp = True
```

This strips `>>>`, `...`, `$`, and `>` prompts so readers copy only the actual commands.

## sphinxcontrib-mermaid

[sphinxcontrib-mermaid](https://sphinxcontrib-mermaid-demo.readthedocs.io/) renders Mermaid diagrams directly in your docs. Lumina automatically adjusts diagram colors to match the current light/dark theme.

### Setup

```bash
uv add sphinxcontrib-mermaid
```

```python
extensions = ["sphinxcontrib.mermaid"]
```

### Dark Mode Support

Lumina handles Mermaid theme switching automatically — diagrams re-render when the user toggles dark mode. No extra configuration needed.

### Usage

Write diagrams with the `mermaid` directive:

```markdown
:::{mermaid}
graph LR
    A[Source] --> B[Build]
    B --> C[Deploy]
:::
```

See [Diagrams](reference/diagrams.md) for flowcharts, sequence diagrams, class diagrams, Gantt charts, and more.

## sphinxcontrib-openapi

[sphinxcontrib-openapi](https://sphinxcontrib-openapi.readthedocs.io/) generates HTTP API documentation directly from OpenAPI (Swagger) specification files. It builds on [sphinxcontrib-httpdomain](https://sphinxcontrib-httpdomain.readthedocs.io/), which provides HTTP method directives for writing endpoint docs by hand. Lumina styles all HTTP endpoints with color-coded method indicators.

### Setup

```bash
uv add sphinxcontrib-openapi
```

```python
extensions = ["sphinxcontrib.openapi"]
```

This also installs the HTTP domain, so you can write individual endpoints manually with `http:get::`, `http:post::`, and other method directives.

### Usage

Point the `openapi` directive at your spec file:

```markdown
```{eval-rst}
.. openapi:: path/to/openapi.yml
```
```

See [HTTP API Documentation](reference/http-api.md) for rendered examples of both auto-generated and manually written HTTP API documentation.

## sphinx-llm

[sphinx-llm](https://github.com/NVIDIA/sphinx-llm) generates LLM-friendly versions of your documentation following the [llms.txt convention](https://llmstxt.org/). This makes your docs directly consumable by AI assistants and coding tools.

It produces three outputs:

- **`llms.txt`** — A markdown index of all pages with titles, URLs, and descriptions
- **`llms-full.txt`** — The full content of every page concatenated into a single markdown file
- **Per-page `.md` files** — Each HTML page gets a companion markdown file (e.g., `getting-started.html.md`)

Lumina automatically adds a `<link rel="alternate">` tag in the HTML `<head>` pointing to `llms.txt` when this extension is detected — no extra configuration needed.

### Setup

```bash
uv add sphinx-llm
```

```python
extensions = ["sphinx_llm.txt"]
```

That’s it. On the next build, `llms.txt`, `llms-full.txt`, and per-page `.md` files will be generated alongside your HTML output.

### Configuration

All options are optional — the defaults work well for most projects:

| Option                    | Default       | Description                                                                                                        |
|---------------------------|---------------|--------------------------------------------------------------------------------------------------------------------|
| `llms_txt_enabled`        | `True`        | Master on/off switch. Disable with `llms_txt_enabled = False`.                                                     |
| `llms_txt_description`    | Auto-detected | Project description shown in the `llms.txt` header. Falls back to `pyproject.toml` description, then `html_title`. |
| `llms_txt_build_parallel` | `True`        | Run the markdown build in parallel with the HTML build.                                                            |
| `llms_txt_suffix_mode`    | `"auto"`      | Controls per-page markdown filenames. Options: `"auto"`, `"file-suffix"`, `"url-suffix"`, `"replace"`.             |
| `llms_txt_full_build`     | `True`        | Whether to generate `llms-full.txt`.                                                                               |

### How It Works

The extension runs a parallel Sphinx build using a markdown builder. This means all directives (including `autodoc`, `toctree`, cross-references) are fully expanded in the output — you get clean, rendered markdown, not raw source.

Each entry in `llms.txt` includes a description sourced from the page’s `meta` description or the first 100 characters of content.

## MathJax

Sphinx includes MathJax support by default. Combined with MyST’s `dollarmath` and `amsmath` extensions, you get full LaTeX math rendering.

### Setup

No additional packages needed. Just enable the MyST extensions:

```python
myst_enable_extensions = [
    "dollarmath",    # $E = mc^2$ inline, $$...$$ display
    "amsmath",       # \begin{aligned}...\end{aligned}
]
```

### Usage

```markdown
Inline math: $f(x) = x^2 + 1$

Display math:

$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

See [Math](reference/math.md) for labeled equations, multi-line systems, and matrices.

## Other Compatible Extensions

Lumina inherits from Sphinx’s `basic` theme, so it works with any extension that targets standard Sphinx output. Some popular ones:

| Extension                  | Purpose                                           |
|----------------------------|---------------------------------------------------|
| `sphinx.ext.autodoc`       | Generate API docs from Python docstrings.         |
| `sphinx.ext.intersphinx`   | Cross-reference objects in other Sphinx projects. |
| `sphinx.ext.viewcode`      | Add links to highlighted source code.             |
| `sphinx.ext.napoleon`      | Support for Google and NumPy docstring styles.    |
| `sphinx.ext.todo`          | Collect and display TODO items.                   |
| `sphinx_autodoc_typehints` | Render type hints in API documentation.           |

## Recommended `conf.py`

Here’s a well-rounded configuration that includes all the recommended extensions:

```python
extensions = [
    # Content
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinxcontrib.mermaid",
    "sphinxcontrib.openapi",

    # LLM-friendly output
    "sphinx_llm.txt",

    # API documentation (if applicable)
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

# MyST configuration
myst_enable_extensions = [
    "colon_fence",
    "dollarmath",
    "amsmath",
    "tasklist",
    "deflist",
    "fieldlist",
    "substitution",
]

# Copy button: strip shell prompts
copybutton_prompt_text = r">>> |\.\.\. |\$ |> "
copybutton_prompt_is_regexp = True

# Intersphinx: link to Python and Sphinx docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}
```
