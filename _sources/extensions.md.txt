# Extensions

Lumina works with any Sphinx extension. This page covers the extensions we recommend and how to configure them for the best experience.

## MyST Parser

[MyST Parser](https://myst-parser.readthedocs.io/) lets you write documentation in Markdown instead of reStructuredText, with full access to Sphinx directives and roles.

### Setup

```bash
uv add myst-parser
```

```{code-block} python
:caption: conf.py
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

````markdown
:::{note}
This is cleaner and easier to type.
:::
````

**Backtick fence** (standard):

````markdown
```{note}
This also works, but nesting gets awkward.
```
````

The colon syntax is especially helpful for nested directives — just add more colons for each level.

## sphinx-design

[sphinx-design](https://sphinx-design.readthedocs.io/) adds cards, grids, tabs, badges, buttons, and dropdowns. Lumina styles all of these components with its own design language.

### Setup

```bash
uv add sphinx-design
```

```{code-block} python
:caption: conf.py
extensions = ["sphinx_design"]
```

### What You Get

::::{grid} 1 1 2 3
:gutter: 3

:::{grid-item-card} Cards
Contained content blocks with optional headers, footers, and links.

See {doc}`reference/cards-and-grids`
:::

:::{grid-item-card} Grids
Responsive layouts with configurable columns per breakpoint.

See {doc}`reference/cards-and-grids`
:::

:::{grid-item-card} Tabs
Tabbed content panels for grouping related information.

See {doc}`reference/code-blocks`
:::

:::{grid-item-card} Badges
Inline status labels with color variants.

See {doc}`reference/badges-and-buttons`
:::

:::{grid-item-card} Buttons
Styled link buttons with primary and secondary variants.

See {doc}`reference/badges-and-buttons`
:::

:::{grid-item-card} Dropdowns
Collapsible content sections.

See {doc}`reference/admonitions`
:::

::::

## sphinx-copybutton

[sphinx-copybutton](https://sphinx-copybutton.readthedocs.io/) adds a copy-to-clipboard button to every code block. Lumina positions and styles it automatically.

### Setup

```bash
uv add sphinx-copybutton
```

```{code-block} python
:caption: conf.py
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

```{code-block} python
:caption: conf.py
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

See {doc}`reference/diagrams` for flowcharts, sequence diagrams, class diagrams, Gantt charts, and more.

## MathJax

Sphinx includes MathJax support by default. Combined with MyST's `dollarmath` and `amsmath` extensions, you get full LaTeX math rendering.

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

See {doc}`reference/math` for labeled equations, multi-line systems, and matrices.

## Other Compatible Extensions

Lumina inherits from Sphinx's `basic` theme, so it works with any extension that targets standard Sphinx output. Some popular ones:

```{list-table}
:header-rows: 1
:widths: 25 75

* - Extension
  - Purpose
* - `sphinx.ext.autodoc`
  - Generate API docs from Python docstrings.
* - `sphinx.ext.intersphinx`
  - Cross-reference objects in other Sphinx projects.
* - `sphinx.ext.viewcode`
  - Add links to highlighted source code.
* - `sphinx.ext.napoleon`
  - Support for Google and NumPy docstring styles.
* - `sphinx.ext.todo`
  - Collect and display TODO items.
* - `sphinx_autodoc_typehints`
  - Render type hints in API documentation.
```

## Recommended `conf.py`

Here's a well-rounded configuration that includes all the recommended extensions:

```{code-block} python
:caption: conf.py — Recommended extensions setup
extensions = [
    # Content
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinxcontrib.mermaid",

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
