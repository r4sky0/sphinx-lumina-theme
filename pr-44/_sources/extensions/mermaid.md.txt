# Mermaid Diagrams

[sphinxcontrib-mermaid](https://sphinxcontrib-mermaid-demo.readthedocs.io/) renders Mermaid diagrams directly in your docs. Lumina automatically adjusts diagram colors to match the current light/dark theme.

## Setup

```bash
uv add sphinxcontrib-mermaid
```

```{code-block} python
:caption: conf.py
extensions = ["sphinxcontrib.mermaid"]
```

## Dark Mode Support

Lumina handles Mermaid theme switching automatically — diagrams re-render when the reader toggles dark mode. No extra configuration needed.

## Usage

Write diagrams with the `mermaid` directive:

````markdown
```{mermaid}
graph LR
    A[Source] --> B[Build]
    B --> C[Deploy]
```
````

See {doc}`/reference/diagrams` for flowcharts, sequence diagrams, class diagrams, Gantt charts, and more.
