# MathJax

Sphinx includes MathJax support by default. Combined with MyST’s `dollarmath` and `amsmath` extensions, you get full LaTeX math rendering.

## Setup

No additional packages needed. Just enable the MyST extensions:

```python
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

See [Math](../reference/math.md) for labeled equations, multi-line systems, and matrices.
