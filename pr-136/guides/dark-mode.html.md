# Dark Mode

Lumina includes dark mode out of the box. Readers can toggle between light, dark, and system preference using the button in the header.

## Configuration

Set the default color mode in your `conf.py`:

```python
html_theme_options = {
    "dark_mode_default": "auto",   # "auto", "light", or "dark"
}
```

`"auto"`
: Follows the reader’s operating system preference. This is the default.

`"light"`
: Forces light mode regardless of system preference.

`"dark"`
: Forces dark mode regardless of system preference.

## How It Works

Lumina toggles dark mode via the `data-theme` attribute on the `<html>` element:

- **Light mode:** `<html data-theme="light">`
- **Dark mode:** `<html data-theme="dark">`

The reader’s choice is persisted in `localStorage` under the key `lumina-theme`. An inline script in the page `<head>` applies the theme before the first paint, preventing any flash of unstyled content (FOUC).

## Customizing Dark Mode Colors

Override the dark mode color palette by targeting the `[data-theme="dark"]` selector in a custom stylesheet.

First, add the stylesheet to your project:

```python
html_static_path = ["_static"]
html_css_files = ["custom.css"]
```

Then override the dark mode properties:

```css
[data-theme="dark"] {
    --lumina-bg: #09090b;
    --lumina-bg-secondary: #18181b;
    --lumina-text: #fafafa;
    --lumina-text-muted: #a1a1aa;
    --lumina-border: #27272a;
    --lumina-accent: #10b981;
    --lumina-accent-light: #022c22;
    --lumina-code-bg: #1c1c20;
}
```
