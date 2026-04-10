# sphinx-llm

[sphinx-llm](https://github.com/NVIDIA/sphinx-llm) generates LLM-friendly versions of your documentation following the [llms.txt convention](https://llmstxt.org/). This makes your docs directly consumable by AI assistants and coding tools.

## What It Produces

- **`llms.txt`** — A markdown index of all pages with titles, URLs, and descriptions
- **`llms-full.txt`** — The full content of every page concatenated into a single markdown file
- **Per-page `.md` files** — Each HTML page gets a companion markdown file (e.g., `getting-started.html.md`)

## Lumina Integration

Lumina automatically adds a `<link rel="alternate">` tag in the HTML `<head>` pointing to `llms.txt` when this extension is detected — no extra configuration needed.

## Setup

```bash
uv add sphinx-llm
```

```{code-block} python
:caption: conf.py
extensions = ["sphinx_llm.txt"]
```

That's it. On the next build, `llms.txt`, `llms-full.txt`, and per-page `.md` files appear alongside your HTML output.

## Configuration

All options are optional — the defaults work well for most projects:

```{list-table}
:header-rows: 1
:widths: 30 15 55

* - Option
  - Default
  - Description
* - `llms_txt_enabled`
  - `True`
  - Master on/off switch. Disable with `llms_txt_enabled = False`.
* - `llms_txt_description`
  - Auto-detected
  - Project description shown in the `llms.txt` header. Falls back to `pyproject.toml` description, then `html_title`.
* - `llms_txt_build_parallel`
  - `True`
  - Run the markdown build in parallel with the HTML build.
* - `llms_txt_suffix_mode`
  - `"auto"`
  - Controls per-page markdown filenames. Options: `"auto"`, `"file-suffix"`, `"url-suffix"`, `"replace"`.
* - `llms_txt_full_build`
  - `True`
  - Whether to generate `llms-full.txt`.
```

## How It Works

The extension runs a parallel Sphinx build using a markdown builder. All directives (including `autodoc`, `toctree`, cross-references) are fully expanded in the output — you get clean, rendered markdown, not raw source.

Each entry in `llms.txt` includes a description sourced from the page's `meta` description or the first 100 characters of content.
