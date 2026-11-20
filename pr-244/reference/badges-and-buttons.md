# Badges & Buttons

Inline badges and clickable buttons from sphinx-design for labeling and calls to action. Requires the `sphinx_design` extension — see [sphinx-design](../extensions/sphinx-design.md) for setup.

## Badges

Inline badges for status labels, version tags, and categories.

plain
primary
secondary
success
warning
danger
info
light
dark

The MyST syntax:

```markdown
{bdg}`plain`
{bdg-primary}`primary`
{bdg-secondary}`secondary`
{bdg-success}`success`
{bdg-warning}`warning`
{bdg-danger}`danger`
{bdg-info}`info`
```

## Outline Badges

Badges with an outline style for a lighter visual weight.

primary
secondary
success
warning
danger
info

The MyST syntax:

```markdown
{bdg-primary-line}`primary`
{bdg-success-line}`success`
```

## Badges in Context

Badges work naturally inline with text: The API is stable and supports Python 3.12+. The old endpoint is deprecated.

## Buttons

Clickable button links for calls to action.

[Get Started](/getting-started/installation)

[View on GitHub](https://github.com)

The MyST syntax:

```markdown
```{button-link} target-url
:color: primary
Button Text
```
```

## Outline Buttons

Buttons with outline styling for secondary actions.

[Get Started](/getting-started/installation)

[View Source](https://github.com)

The MyST syntax:

```markdown
```{button-link} target-url
:color: primary
:outline:
Button Text
```
```

## Button with Reference

Link buttons to internal documentation pages using `button-ref`.

[Read the Guide](../getting-started/installation.md)

The MyST syntax:

```markdown
```{button-ref} page-path
:color: primary
:ref-type: doc
Button Text
```
```

## Practical Examples

### Version and Status Indicators

Document API stability inline: The configuration API is stable, the plugin system is beta, and the WebSocket support is experimental.

### Feature Matrices

| Feature    | Status      | Notes                       |
|------------|-------------|-----------------------------|
| Dark mode  | shipped     | Light, dark, and auto modes |
| i18n       | planned     | Targeted for v2             |
| PDF export | considering | Community request           |

### Call-to-Action Patterns

Use primary buttons for the main action and outline buttons for alternatives:

[Get Started](../getting-started/installation.md)

[View Configuration](../getting-started/configuration.md)
