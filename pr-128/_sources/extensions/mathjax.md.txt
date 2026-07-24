# MathJax

Sphinx includes MathJax support by default. Combined with MyST's `dollarmath` and `amsmath` extensions, you get full LaTeX math rendering.

## Setup

No additional packages needed. Just enable the MyST extensions:

```{code-block} python
:caption: conf.py
myst_enable_extensions = [
    "dollarmath",    # $E = mc^2$ inline, $$...$$ display
    "amsmath",       # \begin{aligned}...\end{aligned}
]
```

## Usage

```markdown
Inline math: $f(x) = x^2 + 1$

Display math:

$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

**Result:**

Inline math: $f(x) = x^2 + 1$

Display math:

$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$

:::{seealso}
{doc}`/reference/math` — labeled equations, multi-line systems, matrices, and symbol tables.
:::
