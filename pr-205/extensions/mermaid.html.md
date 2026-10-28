# Mermaid Diagrams

[sphinxcontrib-mermaid](https://sphinxcontrib-mermaid-demo.readthedocs.io/) renders Mermaid diagrams directly in your docs. Lumina automatically adjusts diagram colors to match the current light/dark theme.

## Setup

```bash
uv add sphinxcontrib-mermaid
```

```python
extensions = ["sphinxcontrib.mermaid"]
```

## Dark Mode Support

Lumina styles diagram labels with Source Sans 3 and uses the theme’s surface, text, and accent colors. The extension re-renders diagrams when the reader toggles dark mode; Lumina preserves their natural size after each render. No extra configuration is needed.

Small diagrams stay at their natural size, while wide diagrams fit the article. Use the **fullscreen ⛶ button** for a larger view and **Escape** to close it. Pan and zoom are optional extension features: enable `mermaid_d3_zoom = True` in `conf.py` if needed.

## Usage

Write diagrams with the `mermaid` directive:

```markdown
```{mermaid}
flowchart LR
    accTitle: From source to published docs
    accDescr: Sphinx builds source files, Lumina styles the pages, and the result is published.
    source[Source files] --> build[Sphinx build]
    build --> theme[Lumina theme]
    theme --> publish([Publish])
```
```

**Result:**

## Emphasize a node

Use Mermaid’s `classDef` to give an important node a stronger outline while retaining the theme’s colors:

```text
classDef ready stroke-width:2px
class publish ready
```

Add these lines inside the diagram after the node definitions. Explicit node fills and strokes are also preserved. If you supply custom colors, check their contrast in both modes.

#### SEE ALSO
[Diagrams](../reference/diagrams.md) — flowcharts, sequence diagrams, class diagrams, Gantt charts, and more rendered examples.
