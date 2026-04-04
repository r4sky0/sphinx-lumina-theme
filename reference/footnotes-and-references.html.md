# Footnotes & References

Cross-referencing, citations, glossaries, and linking across documents and projects.

## Footnotes

Auto-numbered footnotes add citations to the bottom of the page.

Sphinx was created by Georg Brandl<sup>[1](#id3)</sup> and is the de facto standard for Python documentation<sup>[2](#id4)</sup>.

The MyST syntax:

```markdown
Some text with a footnote[^1].

[^1]: Footnote content here.
```

## Cross-References

### Document References

Link to other pages in the documentation using the `{doc}` role.

See the [Typography](typography.md) page for text formatting options, or check out [Code Blocks](code-blocks.md) for syntax highlighting.

The MyST syntax:

```markdown
{doc}`page-name`
{doc}`custom link text <page-name>`
```

<a id="section-label"></a>

### Section References

Create a label above any heading and reference it with `{ref}`.

This section can be referenced from anywhere as [Section References](#section-label).

The MyST syntax:

```markdown
(my-label)=
### My Section

Link to it with {ref}`my-label` or {ref}`custom text <my-label>`.
```

## Glossary

Define terms in a glossary and reference them with the `{term}` role.

<a id="term-MyST"></a>

MyST
: Markedly Structured Text — a Markdown flavor designed for Sphinx that supports directives and roles.

<a id="term-Sphinx"></a>

Sphinx
: A documentation generator that converts reStructuredText and MyST Markdown into HTML, PDF, and other formats.

<a id="term-directive"></a>

directive
: A block-level extension in Sphinx that adds special content like admonitions, code blocks, and tables of contents.

<a id="term-role"></a>

role
: An inline extension in Sphinx that adds semantic meaning to text, such as cross-references, math, and abbreviations.

The [MyST](#term-MyST) parser allows you to write [Sphinx](#term-Sphinx) documentation in Markdown. Use [directives](#term-directive) for block content and [roles](#term-role) for inline content.

The MyST syntax:

```markdown
```{glossary}
Term
  Definition of the term.
```

Reference it with {term}`Term`.
```

## Download Links

Provide downloadable files with the `{download}` role.

Download the sample configuration: [`example.json`](example.json).

The MyST syntax:

```markdown
{download}`example.json`
{download}`custom text <example.json>`
```

## Substitutions

Define reusable text snippets in `conf.py` and use them across pages.

This documentation is for Sphinx Lumina Theme version 1.22.0.

The MyST syntax:

```markdown
This is for {{project_name}} version {{version}}.
```

Substitutions are defined in `conf.py`:

```python
myst_substitutions = {
    "project_name": "Sphinx Lumina Theme",
    "version": "0.1.0",
}
```

## Version Directives

Document when features were added, changed, or deprecated.

#### Versionadded
Added in version 1.2.0: The `nav_links` option now supports dropdown menus via the `children` key.

#### Versionchanged
Changed in version 1.5.0: The `search_backend` option now defaults to `"pagefind"` instead of `"sphinx"`.

#### Deprecated
Deprecated since version 1.8.0: The `legacy_search` option. Use `search_backend` instead.

The MyST syntax:

```markdown
```{versionadded} 0.1.0
Description of what was added.
```

```{versionchanged} 0.2.0
Description of what changed.
```

```{deprecated} 0.3.0
Description of what was deprecated.
```
```

## Intersphinx

Link to objects in other Sphinx documentation projects — Python standard library, third-party packages, or your own related projects.

### Setup

```python
extensions = ["sphinx.ext.intersphinx"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}
```

### Usage

Reference any documented object from the mapped project:

```markdown
See {py:class}`python:pathlib.Path` for path manipulation.

Read about {doc}`sphinx:usage/configuration` for conf.py options.

The {py:func}`python:json.dumps` function serializes Python objects to JSON.
```

### Finding Available References

List all objects available from an intersphinx mapping:

```bash
python -m sphinx.ext.intersphinx https://docs.python.org/3/objects.inv
```

This outputs every referenceable object, which you can search for the exact role and name to use.

---
* <a id='id3'>**[1]**</a> Georg Brandl started the Sphinx project in 2008 as a successor to Python’s previous documentation toolchain.
* <a id='id4'>**[2]**</a> Over 85% of Python packages on PyPI use Sphinx for their documentation.
