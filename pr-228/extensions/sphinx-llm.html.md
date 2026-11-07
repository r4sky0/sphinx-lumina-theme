# sphinx-llm

Make your docs readable by AI assistants and coding tools. [sphinx-llm](https://github.com/NVIDIA/sphinx-llm) generates LLM-friendly versions of your documentation following the [llms.txt convention](https://llmstxt.org/) — Lumina links to `llms.txt` automatically once the extension is enabled.

## What It Produces

- **`llms.txt`** — A markdown index of all pages with titles, URLs, and descriptions, plus a scoped `llms.txt` in each section folder
- **`llms-full.txt`** — The full content of every page concatenated into a single markdown file (opt-in, see `llms_txt_full_build`)
- **Per-page `.md` files** — Each HTML page gets a companion markdown file (e.g., `getting-started.html.md` and `getting-started.md`)

## Lumina Integration

Lumina automatically adds a `<link rel="alternate">` tag in the HTML `<head>` pointing to `llms.txt` when this extension is detected — no extra configuration needed. sphinx-llm 1.1 and later also add their own `<link rel="describedby">` tag.

## Setup

```bash
uv add sphinx-llm
```

```python
extensions = ["sphinx_llm.txt"]
```

That’s it. On the next build, `llms.txt` and per-page `.md` files appear alongside your HTML output.

Lumina’s own documentation builds with `-W` and also sets these options:

```python
llms_txt_full_build = True
# Skip nodes the Markdown export can't render (tips, sidebars, diagrams)
# instead of warning about each one.
llms_txt_suppress_unknown_node_warnings = True
```

## Configuration

All options are optional — the defaults work well for most projects:

| Option                                    | Default       | Description                                                                                                                                                                                               |
|-------------------------------------------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `llms_txt_enabled`                        | `True`        | Master on/off switch. Disable with `llms_txt_enabled = False`.                                                                                                                                            |
| `llms_txt_description`                    | Auto-detected | Project description shown in the `llms.txt` header. Falls back to `pyproject.toml` description, then `html_title`.                                                                                        |
| `llms_txt_build_parallel`                 | `True`        | Run the markdown build in parallel with the HTML build.                                                                                                                                                   |
| `llms_txt_suffix_mode`                    | `"auto"`      | Controls per-page markdown filenames: `"append"` writes `page.html.md`, `"replace"` writes `page.md`, and `"auto"` writes both. `"file-suffix"` and `"url-suffix"` are deprecated aliases for `"append"`. |
| `llms_txt_full_build`                     | `False`       | Whether to generate `llms-full.txt`. Before sphinx-llm 1.1 this defaulted to `True`.                                                                                                                      |
| `llms_txt_exclude`                        | `[]`          | Glob patterns of document names (e.g. `"internal/*"`) to leave out of the `llms.txt` outputs.                                                                                                             |
| `llms_txt_suppress_unknown_node_warnings` | `False`       | Skip document nodes the Markdown export can’t render without warning. `True` silences all of them; a list of node class names silences only those.                                                        |

## How It Works

The extension runs a parallel Sphinx build using a markdown builder. All directives (including `autodoc`, `toctree`, cross-references) are fully expanded in the output — you get clean, rendered markdown, not raw source.

Each entry in `llms.txt` includes a description sourced from the page’s `meta` description or the first 100 characters of content.
