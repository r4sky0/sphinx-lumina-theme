# Images & Figures

Embedding and formatting visual content in your documentation.

## Basic Images

Use standard Markdown syntax to embed an image.

![Wide placeholder image](reference/_images/placeholder-wide.svg)

The MyST syntax:

```markdown
![Alt text](path/to/image.png)
```

## Image Directive

The `image` directive gives you control over width, alignment, and alt text that Markdown syntax doesn’t offer.

![Square placeholder image](reference/_images/placeholder-square.svg)

The MyST syntax:

```markdown
```{image} path/to/image.svg
:alt: Description of the image
:width: 200px
:align: center
```
```

### Alignment Options

Images can be aligned left, center, or right within the content area.

![Left-aligned image](reference/_images/placeholder-square.svg)

**Left** — text wraps around the right side.

![Centered image](reference/_images/placeholder-square.svg)

**Center** — image stands alone.

![Right-aligned image](reference/_images/placeholder-square.svg)

**Right** — text wraps around the left side.

### Wrapping Text Around Images

Left- and right-aligned images float, so the paragraphs that follow wrap around them. Floats end at the next heading, and on narrow screens the image stacks above the text.

![Right-aligned image with wrapping text](reference/_images/placeholder-square.svg)

Lumina keeps the gutter between a floated image and the text at the same spacing as other blocks, so the column stays easy to scan. This paragraph and the next wrap around the image on the right. Put the image just before the text it illustrates, and keep it small enough that a few lines still fit beside it.

A centered image or figure stands alone, with its caption centered underneath. Use centering for diagrams that need the full attention of the reader, and floats for supporting pictures.

The MyST syntax:

```markdown
```{image} path/to/image.png
:alt: Description
:width: 160px
:align: right
```

Text that wraps around the image.
```

## Figures

Figures wrap an image with a caption and optional legend. Use them when an image needs explanation or attribution.

![Wide placeholder image](reference/_images/placeholder-wide.svg)

The MyST syntax:

```markdown
```{figure} path/to/image.svg
:alt: Description
:width: 100%
:align: center

Caption text with **Markdown** support.
```
```

## Scaled Images

Control image size as a percentage of the containing block’s width.

![Image filling its grid item](reference/_images/placeholder-square.svg)

`100%` of the grid item

![Half-width image](reference/_images/placeholder-square.svg)

`50%` width

![Quarter-width image](reference/_images/placeholder-square.svg)

`25%` width

You can use percentages, pixels, or any CSS length unit:

```markdown
:width: 50%       # Percentage of content width
:width: 300px     # Fixed pixel width
:width: 20em      # Relative to font size
```

## Linked Images

Wrap an image in a link to make it clickable.

[![Placeholder image](reference/_images/placeholder-square.svg)](_images/placeholder-wide.svg)

The MyST syntax:

```markdown
[![Alt text](thumbnail.png)](full-size.png)
```

## Images in Admonitions

Images work inside any block element, including admonitions and cards.

#### NOTE
Images inside admonitions maintain their styling. This is useful for annotated screenshots or diagrams that accompany a specific instruction.

![Image inside an admonition](reference/_images/placeholder-wide.svg)

## File Format Guidance

Choose the right format for your images:

| Format   | Best for                 | Notes                                                                                                                            |
|----------|--------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| **SVG**  | Diagrams, icons, logos   | Scales to any size without quality loss. Smallest file size for simple graphics. Preferred for anything that isn’t a photograph. |
| **PNG**  | Screenshots, UI captures | Lossless compression. Good for images with text, sharp edges, or transparency.                                                   |
| **WebP** | Photos, complex images   | Modern format with excellent compression. Supported by all current browsers.                                                     |
| **JPEG** | Photos (fallback)        | Wide compatibility. Use WebP instead when possible for smaller files.                                                            |
