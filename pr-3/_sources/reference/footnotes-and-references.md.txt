# Footnotes & References

Cross-referencing, citations, glossaries, and linking across documents and projects.

## Footnotes

Auto-numbered footnotes add citations to the bottom of the page.

Sphinx was created by Georg Brandl[^1] and is the de facto standard for Python documentation[^2].

[^1]: Georg Brandl started the Sphinx project in 2008 as a successor to Python's previous documentation toolchain.

[^2]: Over 85% of Python packages on PyPI use Sphinx for their documentation.

The MyST syntax:

```markdown
Some text with a footnote[^1].

[^1]: Footnote content here.
```

## Cross-References

### Document References

Link to other pages in the documentation using the `{doc}` role.

See the {doc}`typography` page for text formatting options, or check out {doc}`code-blocks` for syntax highlighting.

The MyST syntax:

```markdown
{doc}`page-name`
{doc}`custom link text <page-name>`
```

(section-label)=
### Section References

Create a label above any heading and reference it with `{ref}`.

This section can be referenced from anywhere as {ref}`section-label`.

The MyST syntax:

```markdown
(my-label)=
### My Section

Link to it with {ref}`my-label` or {ref}`custom text <my-label>`.
```

## Glossary

Define terms in a glossary and reference them with the `{term}` role.

```{glossary}
MyST
  Markedly Structured Text — a Markdown flavor designed for Sphinx that supports directives and roles.

Sphinx
  A documentation generator that converts reStructuredText and MyST Markdown into HTML, PDF, and other formats.

directive
  A block-level extension in Sphinx that adds special content like admonitions, code blocks, and tables of contents.

role
  An inline extension in Sphinx that adds semantic meaning to text, such as cross-references, math, and abbreviations.
```

The {term}`MyST` parser allows you to write {term}`Sphinx` documentation in Markdown. Use {term}`directives <directive>` for block content and {term}`roles <role>` for inline content.

The MyST syntax:

~~~markdown
```{glossary}
Term
  Definition of the term.
```

Reference it with {term}`Term`.
~~~

## Download Links

Provide downloadable files with the `{download}` role.

Download the sample configuration: {download}`example.json`.

The MyST syntax:

```markdown
{download}`example.json`
{download}`custom text <example.json>`
```

## Substitutions

Define reusable text snippets in `conf.py` and use them across pages.

This documentation is for {{project_name}} version {{version}}.

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

```{versionadded} 0.1.0
The `accent_color` theme option for customizing the primary color.
```

```{versionchanged} 0.2.0
The `search_backend` option now defaults to `"pagefind"` instead of `"sphinx"`.
```

```{deprecated} 0.3.0
The `logo_only` option. Use the `logo` configuration in `html_theme_options` instead.
```

The MyST syntax:

~~~markdown
```{versionadded} 0.1.0
Description of what was added.
```

```{versionchanged} 0.2.0
Description of what changed.
```

```{deprecated} 0.3.0
Description of what was deprecated.
```
~~~

## Intersphinx

Link to objects in other Sphinx documentation projects — Python standard library, third-party packages, or your own related projects.

### Setup

```{code-block} python
:caption: conf.py
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

:::{tip}
Use `python:` as a prefix to avoid conflicts when your own project defines objects with the same name as Python built-ins.
:::

### Finding Available References

List all objects available from an intersphinx mapping:

```bash
python -m sphinx.ext.intersphinx https://docs.python.org/3/objects.inv
```

This outputs every referenceable object, which you can search for the exact role and name to use.
