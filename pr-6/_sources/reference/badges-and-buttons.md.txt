# Badges & Buttons

Inline badges and clickable buttons from sphinx-design for labeling and calls to action. Requires the `sphinx_design` extension — see {doc}`../extensions` for setup.

## Badges

Inline badges for status labels, version tags, and categories.

{bdg}`plain`
{bdg-primary}`primary`
{bdg-secondary}`secondary`
{bdg-success}`success`
{bdg-warning}`warning`
{bdg-danger}`danger`
{bdg-info}`info`
{bdg-light}`light`
{bdg-dark}`dark`

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

{bdg-primary-line}`primary`
{bdg-secondary-line}`secondary`
{bdg-success-line}`success`
{bdg-warning-line}`warning`
{bdg-danger-line}`danger`
{bdg-info-line}`info`

The MyST syntax:

```markdown
{bdg-primary-line}`primary`
{bdg-success-line}`success`
```

## Badges in Context

Badges work naturally inline with text: The API is {bdg-success}`stable` and supports Python {bdg-info}`3.10+`. The old endpoint is {bdg-warning}`deprecated`.

## Buttons

Clickable button links for calls to action.

```{button-link} ../getting-started
:color: primary
Get Started
```

```{button-link} https://github.com
:color: secondary
View on GitHub
```

The MyST syntax:

~~~markdown
```{button-link} target-url
:color: primary
Button Text
```
~~~

## Outline Buttons

Buttons with outline styling for secondary actions.

```{button-link} ../getting-started
:color: primary
:outline:
Get Started
```

```{button-link} https://github.com
:color: secondary
:outline:
View Source
```

The MyST syntax:

~~~markdown
```{button-link} target-url
:color: primary
:outline:
Button Text
```
~~~

## Button with Reference

Link buttons to internal documentation pages using `button-ref`.

```{button-ref} ../getting-started
:color: primary
:ref-type: doc
Read the Guide
```

The MyST syntax:

~~~markdown
```{button-ref} page-path
:color: primary
:ref-type: doc
Button Text
```
~~~

## Practical Examples

### Version and Status Indicators

Document API stability inline: The configuration API is {bdg-success}`stable`, the plugin system is {bdg-warning}`beta`, and the WebSocket support is {bdg-info}`experimental`.

### Feature Matrices

```{list-table}
:header-rows: 1
:widths: 40 20 40

* - Feature
  - Status
  - Notes
* - Dark mode
  - {bdg-success}`shipped`
  - Light, dark, and auto modes
* - i18n
  - {bdg-warning}`planned`
  - Targeted for v2
* - PDF export
  - {bdg-secondary}`considering`
  - Community request
```

### Call-to-Action Patterns

Use primary buttons for the main action and outline buttons for alternatives:

```{button-ref} ../getting-started
:color: primary
:ref-type: doc
Get Started
```

```{button-ref} ../customization
:color: secondary
:outline:
:ref-type: doc
View Configuration
```

:::{tip}
- Use **badges** for inline labels — status, versions, categories
- Use **buttons** for navigation — "Get Started", "View Source", "Download"
- Use **primary** color for the single most important action on a page
- Use **outline** or **secondary** for supplementary actions
:::
