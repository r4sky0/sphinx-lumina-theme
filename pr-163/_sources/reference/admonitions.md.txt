# Admonitions

Callout boxes that highlight important information. Each type has a distinct color and icon.

## Standard Types

### Note

:::{note}
This is a **note** admonition. Use it for supplementary information the reader might find useful.
:::

### Tip

:::{tip}
This is a **tip** admonition. Use it for helpful suggestions and best practices.
:::

### Warning

:::{warning}
This is a **warning** admonition. Use it to alert readers about potential pitfalls.
:::

### Danger

:::{danger}
This is a **danger** admonition. Use it for critical warnings that could cause data loss or security issues.
:::

### Important

:::{important}
This is an **important** admonition. Use it for key information the reader must not miss.
:::

### Caution

:::{caution}
This is a **caution** admonition. Use it for actions that need care but aren't dangerous.
:::

### See Also

:::{seealso}
Check out the {doc}`typography` page for text formatting options.
:::

### Hint

:::{hint}
This is a **hint** admonition. Use it for subtle guidance or clues.
:::

### Error

:::{error}
This is an **error** admonition. Use it to document error conditions or common failure modes.
:::

### Attention

:::{attention}
This is an **attention** admonition. Use it when something requires the reader's immediate focus.
:::

The MyST syntax for any admonition type:

```markdown
:::{note}
Content goes here with **Markdown** support.
:::
```

## Custom Titles

Override the default title with the `admonition` directive.

:::{admonition} Did You Know?
Sphinx supports over 10 built-in admonition types, and you can create custom ones with any title you like.
:::

:::{admonition} Breaking Change
:class: danger
You can also apply a type's styling to a custom-titled admonition using the `:class:` option.
:::

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

:::{tip}
Here's a configuration example inside an admonition:

```python
html_theme_options = {
    "accent_color": "#10b981",
    "dark_mode_default": "auto",
}
```

Key points:

- Use `accent_color` to customize the primary color
- Set `dark_mode_default` to `"auto"` for system preference detection
:::

## Nested Admonitions

Admonitions can be nested by increasing the number of colons.

::::{warning}
This is an outer warning.

:::{tip}
This tip is nested inside the warning. Use nested admonitions sparingly — they can be hard to follow.
:::
::::

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

:::{dropdown} Click to expand
This content is hidden by default. Dropdowns are useful for lengthy details, optional context, or spoilers.

- Item one
- Item two
- Item three
:::

:::{dropdown} Open by default
:open:
This dropdown starts expanded. Use the `:open:` option when the content is important but you still want the collapsible behavior.
:::

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
