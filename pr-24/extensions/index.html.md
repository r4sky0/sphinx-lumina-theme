# Extensions

Lumina works with any Sphinx extension. These are the ones we recommend and style specifically.

Write documentation in Markdown with full Sphinx directive support.

Cards, grids, tabs, badges, buttons, and dropdowns.

Copy-to-clipboard button on every code block.

Flowcharts, sequence diagrams, class diagrams, and more.

Auto-generated HTTP API docs from OpenAPI specs.

LLM-friendly docs following the llms.txt convention.

LaTeX math rendering with MathJax.

## Other Compatible Extensions

Lumina inherits from Sphinx’s `basic` theme, so it works with any extension that targets standard Sphinx output:

| Extension                  | Purpose                                           |
|----------------------------|---------------------------------------------------|
| `sphinx.ext.autodoc`       | Generate API docs from Python docstrings.         |
| `sphinx.ext.intersphinx`   | Cross-reference objects in other Sphinx projects. |
| `sphinx.ext.viewcode`      | Add links to highlighted source code.             |
| `sphinx.ext.napoleon`      | Support for Google and NumPy docstring styles.    |
| `sphinx.ext.todo`          | Collect and display TODO items.                   |
| `sphinx_autodoc_typehints` | Render type hints in API documentation.           |

## Recommended `conf.py`

A well-rounded configuration that includes all the recommended extensions:

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
