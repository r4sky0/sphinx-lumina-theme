# sphinx-copybutton

[sphinx-copybutton](https://sphinx-copybutton.readthedocs.io/) adds a copy-to-clipboard button to every code block. Lumina positions and styles it automatically.

## Setup

```bash
uv add sphinx-copybutton
```

```python
extensions = ["sphinx_copybutton"]
```

No additional configuration needed. The button appears on hover in the top-right corner of any code block — try it on any example on this page.

## Filtering Prompt Characters

If your code blocks include shell prompts (e.g., `$` for bash, `>>>` for Python REPL), configure the extension to strip them when copying:

```python
copybutton_prompt_text = r">>> |\.\.\. |\$ |> "
copybutton_prompt_is_regexp = True
```

This strips `>>>`, `...`, `$`, and `>` prompts so readers copy only the actual commands.

#### SEE ALSO
[Code Blocks](../reference/code-blocks.md) — for syntax highlighting, line numbers, captions, diffs, and tabbed code examples.
