# Welcome

This is a test document used by the sphinx-lumina-theme test suite to verify rendering and metadata behaviour.

## Section One

Some content here.

## Section Two

More content here.

### Subsection

Nested content.

## Admonitions

:::{note}
This is a note admonition.
:::

:::{tip}
This is a tip admonition.
:::

:::{warning}
This is a warning admonition.
:::

:::{danger}
This is a danger admonition.
:::

## Code Examples

```python
def hello(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"
```

## Tabs

::::{tab-set}
:::{tab-item} Python
```python
print("Hello")
```
:::
:::{tab-item} JavaScript
```javascript
console.log("Hello");
```
:::
::::

## Cards

::::{grid} 2
:::{grid-item-card} Card One
Content one.
:::
:::{grid-item-card} Card Two
Content two.
:::
::::

```{toctree}
:hidden:
getting-started
typography-test
landing-test
icons-test
guides/index
seo-described
seo-keywords
seo-image-override
seo-noindex
```
