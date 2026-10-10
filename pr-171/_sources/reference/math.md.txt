# Math

Mathematical notation rendered by MathJax. Enabled by the `dollarmath` and `amsmath` MyST extensions.

:::{note}
See {doc}`/extensions/mathjax` for setup instructions.
:::

## Inline Math

Embed math expressions within a line of text.

The equation $E = mc^2$ describes mass-energy equivalence. The quadratic formula is $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$.

The MyST syntax:

```markdown
The equation $E = mc^2$ is inline math.
```

## Display Math

Standalone equations centered on their own line.

$$
\int_{-\infty}^{\infty} e^{-x^2} \, dx = \sqrt{\pi}
$$

$$
\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}
$$

The MyST syntax:

```markdown
$$
\int_{-\infty}^{\infty} e^{-x^2} \, dx = \sqrt{\pi}
$$
```

## Labeled Equations

Add a label to reference an equation elsewhere in the document.

```{math}
:label: euler
e^{i\pi} + 1 = 0
```

Euler's identity is shown in equation {eq}`euler`.

The MyST syntax:

~~~markdown
```{math}
:label: euler
e^{i\pi} + 1 = 0
```

See equation {eq}`euler`.
~~~

## Multi-line Equations

Use the `amsmath` environment for aligned multi-line equations.

```{math}
:label: maxwell
\begin{aligned}
\nabla \cdot \mathbf{E} &= \frac{\rho}{\varepsilon_0} \\
\nabla \cdot \mathbf{B} &= 0 \\
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \\
\nabla \times \mathbf{B} &= \mu_0 \mathbf{J} + \mu_0 \varepsilon_0 \frac{\partial \mathbf{E}}{\partial t}
\end{aligned}
```

Maxwell's equations {eq}`maxwell` describe classical electromagnetism.

## Piecewise Functions

$$
f(x) = \begin{cases}
x^2 & \text{if } x \geq 0 \\
-x & \text{if } x < 0
\end{cases}
$$

The MyST syntax:

```markdown
$$
f(x) = \begin{cases}
x^2 & \text{if } x \geq 0 \\
-x & \text{if } x < 0
\end{cases}
$$
```

## Matrix Notation

$$
A = \begin{pmatrix}
a_{11} & a_{12} & a_{13} \\
a_{21} & a_{22} & a_{23} \\
a_{31} & a_{32} & a_{33}
\end{pmatrix}
$$

Different bracket styles:

| Syntax | Brackets | Result |
|--------|----------|--------|
| `pmatrix` | Parentheses | $\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}$ |
| `bmatrix` | Square | $\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}$ |
| `vmatrix` | Vertical bars | $\begin{vmatrix} 1 & 2 \\ 3 & 4 \end{vmatrix}$ |

## Limits and Series

$$
\lim_{n \to \infty} \left(1 + \frac{1}{n}\right)^n = e
$$

$$
\prod_{i=1}^{n} x_i = x_1 \cdot x_2 \cdots x_n
$$

## Common Symbols Reference

### Greek Letters

| Lowercase | Command | Uppercase | Command |
|-----------|---------|-----------|---------|
| $\alpha$ | `\alpha` | $A$ | `A` |
| $\beta$ | `\beta` | $B$ | `B` |
| $\gamma$ | `\gamma` | $\Gamma$ | `\Gamma` |
| $\delta$ | `\delta` | $\Delta$ | `\Delta` |
| $\epsilon$ | `\epsilon` | $E$ | `E` |
| $\lambda$ | `\lambda` | $\Lambda$ | `\Lambda` |
| $\mu$ | `\mu` | $M$ | `M` |
| $\pi$ | `\pi` | $\Pi$ | `\Pi` |
| $\sigma$ | `\sigma` | $\Sigma$ | `\Sigma` |
| $\omega$ | `\omega` | $\Omega$ | `\Omega` |

### Operators and Relations

| Symbol | Command | Symbol | Command |
|--------|---------|--------|---------|
| $\leq$ | `\leq` | $\geq$ | `\geq` |
| $\neq$ | `\neq` | $\approx$ | `\approx` |
| $\pm$ | `\pm` | $\times$ | `\times` |
| $\div$ | `\div` | $\cdot$ | `\cdot` |
| $\in$ | `\in` | $\notin$ | `\notin` |
| $\subset$ | `\subset` | $\subseteq$ | `\subseteq` |
| $\cup$ | `\cup` | $\cap$ | `\cap` |
| $\infty$ | `\infty` | $\partial$ | `\partial` |
| $\nabla$ | `\nabla` | $\forall$ | `\forall` |

### Arrows

| Symbol | Command | Symbol | Command |
|--------|---------|--------|---------|
| $\rightarrow$ | `\rightarrow` | $\leftarrow$ | `\leftarrow` |
| $\Rightarrow$ | `\Rightarrow` | $\Leftarrow$ | `\Leftarrow` |
| $\leftrightarrow$ | `\leftrightarrow` | $\Leftrightarrow$ | `\Leftrightarrow` |
| $\mapsto$ | `\mapsto` | $\implies$ | `\implies` |

:::{tip}
- Use `\text{}` to include words inside math: $P(\text{error}) < 0.05$
- Use `\mathbf{}` for bold vectors: $\mathbf{v} = (v_1, v_2, v_3)$
- Use `\,` for thin spacing and `\quad` for wider spacing inside equations
:::
