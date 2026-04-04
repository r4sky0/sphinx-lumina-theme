# sphinx-copybutton

[sphinx-copybutton](https://sphinx-copybutton.readthedocs.io/) adds a copy-to-clipboard button to every code block. Lumina positions and styles it automatically.

## Setup

```bash
uv add sphinx-copybutton
```

```{code-block} python
:caption: conf.py
extensions = ["sphinx_copybutton"]
```

No additional configuration needed. The button appears on hover in the top-right corner of any code block.

## Filtering Prompt Characters

If your code blocks include shell prompts, configure the extension to strip them when copying:

```{code-block} python
:caption: conf.py
copybutton_prompt_text = r">>> |\.\.\. |\$ |> "
copybutton_prompt_is_regexp = True
```

This strips `>>>`, `...`, `$`, and `>` prompts so readers copy only the actual commands.
