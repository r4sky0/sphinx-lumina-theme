# MyST Parser

[MyST Parser](https://myst-parser.readthedocs.io/) lets you write documentation in Markdown instead of reStructuredText, with full access to Sphinx directives and roles.

## Setup

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

:::{tip}
For writing syntax, colon fence usage, and substitutions, see the {doc}`/guides/myst-markdown` guide.
:::
