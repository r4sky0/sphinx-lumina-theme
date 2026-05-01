# Images & Figures

Embedding and formatting visual content in your documentation.

:::{tip}
Click any image on this page to view it full-size in an overlay. Disable site-wide with `image_lightbox = "false"`, or per-image with the `no-lightbox` CSS class. Linked images (`<a>`-wrapped) keep their navigation behaviour.
:::

## Basic Images

Use standard Markdown syntax to embed an image.

![Wide placeholder image](_images/placeholder-wide.svg)

The MyST syntax:

```markdown
![Alt text](path/to/image.png)
```

:::{tip}
Always include descriptive alt text. It improves accessibility for screen reader users and appears as fallback text if the image fails to load.
:::

## Image Directive

The `image` directive gives you control over width, alignment, and alt text that Markdown syntax doesn't offer.

```{image} _images/placeholder-square.svg
:alt: Square placeholder image
:width: 200px
:align: center
```

The MyST syntax:

~~~markdown
```{image} path/to/image.svg
:alt: Description of the image
:width: 200px
:align: center
```
~~~

### Alignment Options

Images can be aligned left, center, or right within the content area.

::::{grid} 3

:::{grid-item}
```{image} _images/placeholder-square.svg
:alt: Left-aligned image
:width: 120px
:align: left
```
**Left** — text wraps around the right side.
:::

:::{grid-item}
```{image} _images/placeholder-square.svg
:alt: Centered image
:width: 120px
:align: center
```
**Center** — image stands alone.
:::

:::{grid-item}
```{image} _images/placeholder-square.svg
:alt: Right-aligned image
:width: 120px
:align: right
```
**Right** — text wraps around the left side.
:::

::::

## Figures

Figures wrap an image with a caption and optional legend. Use them when an image needs explanation or attribution.

```{figure} _images/placeholder-wide.svg
:alt: Wide placeholder image
:width: 100%
:align: center

**Figure 1.** A wide placeholder image demonstrating the figure directive. Figures support full Markdown in captions including **bold**, *italic*, and `code`.
```

The MyST syntax:

~~~markdown
```{figure} path/to/image.svg
:alt: Description
:width: 100%
:align: center

Caption text with **Markdown** support.
```
~~~

:::{tip}
Use figures instead of bare images when you need a caption. Figures are also the correct semantic choice for diagrams, screenshots, and charts — anything that the text refers to by number or name.
:::

## Scaled Images

Control image size as a percentage of the content width.

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item}
```{image} _images/placeholder-square.svg
:alt: Full-width image
:width: 100%
```
`100%` width
:::

:::{grid-item}
```{image} _images/placeholder-square.svg
:alt: Half-width image
:width: 100%
```
`50%` width
:::

:::{grid-item}
```{image} _images/placeholder-square.svg
:alt: Quarter-width image
:width: 100%
```
`25%` width
:::

::::

You can use percentages, pixels, or any CSS length unit:

```markdown
:width: 50%       # Percentage of content width
:width: 300px     # Fixed pixel width
:width: 20em      # Relative to font size
```

## Linked Images

Wrap an image in a link to make it clickable.

[![Placeholder image](_images/placeholder-square.svg)](_images/placeholder-wide.svg)

The MyST syntax:

```markdown
[![Alt text](thumbnail.png)](full-size.png)
```

## Images in Admonitions

Images work inside any block element, including admonitions and cards.

:::{note}
Images inside admonitions maintain their styling. This is useful for annotated screenshots or diagrams that accompany a specific instruction.

```{image} _images/placeholder-wide.svg
:alt: Image inside an admonition
:width: 100%
```
:::

## File Format Guidance

Choose the right format for your images:

```{list-table}
:header-rows: 1
:widths: 15 25 60

* - Format
  - Best for
  - Notes
* - **SVG**
  - Diagrams, icons, logos
  - Scales to any size without quality loss. Smallest file size for simple graphics. Preferred for anything that isn't a photograph.
* - **PNG**
  - Screenshots, UI captures
  - Lossless compression. Good for images with text, sharp edges, or transparency.
* - **WebP**
  - Photos, complex images
  - Modern format with excellent compression. Supported by all current browsers.
* - **JPEG**
  - Photos (fallback)
  - Wide compatibility. Use WebP instead when possible for smaller files.
```

:::{tip}
Store images in a `_images/` subdirectory within your docs folder to keep things organized. Reference them with relative paths: `_images/my-screenshot.png`.
:::
