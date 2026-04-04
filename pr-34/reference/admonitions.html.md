# Admonitions

Callout boxes that highlight important information. Each type has a distinct color and icon.

## Standard Types

### Note

#### NOTE
This is a **note** admonition. Use it for supplementary information the reader might find useful.

### Tip

### Warning

#### WARNING
This is a **warning** admonition. Use it to alert readers about potential pitfalls.

### Danger

### Important

#### IMPORTANT
This is an **important** admonition. Use it for key information the reader must not miss.

### Caution

### See Also

#### SEE ALSO
Check out the [Typography](typography.md) page for text formatting options.

### Hint

#### HINT
This is a **hint** admonition. Use it for subtle guidance or clues.

### Error

### Attention

#### ATTENTION
This is an **attention** admonition. Use it when something requires the reader’s immediate focus.

The MyST syntax for any admonition type:

```markdown
:::{note}
Content goes here with **Markdown** support.
:::
```

## Custom Titles

Override the default title with the `admonition` directive.

The MyST syntax:

```markdown
:::{admonition} Custom Title
Content here.
:::

:::{admonition} Styled Custom Title
:class: danger
This uses danger styling with a custom title.
:::
```

## Rich Content Inside Admonitions

Admonitions can contain any content — code blocks, lists, tables, and more.

## Nested Admonitions

Admonitions can be nested by increasing the number of colons.

#### WARNING
This is an outer warning.

The MyST syntax (note the extra colon on the outer directive):

```markdown
::::{warning}
Outer admonition.

:::{tip}
Inner admonition.
:::
::::
```

## Dropdown Admonitions

Use the sphinx-design `dropdown` directive for collapsible content.

### Click to expand

This content is hidden by default. Dropdowns are useful for lengthy details, optional context, or spoilers.

- Item one
- Item two
- Item three

### Open by default

This dropdown starts expanded. Use the `:open:` option when the content is important but you still want the collapsible behavior.

The MyST syntax:

```markdown
:::{dropdown} Click to expand
Hidden content here.
:::

:::{dropdown} Open by default
:open:
Expanded content here.
:::
```
