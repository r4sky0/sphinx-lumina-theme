# MyST Markdown

Write Sphinx documentation in Markdown with full access to directives and roles.

Lumina works with both reStructuredText and [MyST Markdown](https://myst-parser.readthedocs.io/). We recommend MyST for a more natural writing experience.

## Setup

::::{tab-set}

:::{tab-item} uv (recommended)
```bash
uv add myst-parser
```
:::

:::{tab-item} pip
```bash
pip install myst-parser
```
:::

::::

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

## Writing in MyST

Write your docs in `.md` files instead of `.rst`:

```markdown
# My Page Title

This is a paragraph with **bold** and `code`.

:::{note}
Admonitions use the colon fence syntax.
:::
```

## Colon Fence Syntax

The `colon_fence` extension gives you a cleaner syntax for directives.

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

The colon syntax is especially helpful for nested directives — just add more colons for each level:

````markdown
::::{warning}
Outer admonition.

:::{tip}
Inner admonition.
:::
::::
````

## Substitutions

Define reusable variables in `conf.py` and use them across pages:

```{code-block} python
:caption: conf.py
myst_substitutions = {
    "project_name": "My Project",
    "version": "1.0.0",
}
```

Use them in any `.md` file:

```markdown
Welcome to {{project_name}} version {{version}}.
```

## Available Extensions

```{list-table}
:header-rows: 1
:widths: 25 75

* - Extension
  - Description
* - `colon_fence`
  - Use `:::` for directives instead of backtick fences. Cleaner nesting.
* - `dollarmath`
  - `$inline$` and `$$display$$` LaTeX math syntax.
* - `amsmath`
  - Multi-line equation environments like `\begin{aligned}`.
* - `tasklist`
  - `- [x]` checkbox task lists.
* - `deflist`
  - Definition lists with `Term\n: Definition` syntax.
* - `fieldlist`
  - `:Key: Value` metadata lists.
* - `substitution`
  - `{{variable}}` template replacements defined in `conf.py`.
```

:::{tip}
For installation and configuration details, see {doc}`/extensions/myst-parser`.
:::
