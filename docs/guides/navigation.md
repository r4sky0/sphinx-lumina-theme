# Navigation

Configure header links, social icons, sidebar depth, and breadcrumbs.

## Header Navigation Links

Add links to your site header for quick access to key pages:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "nav_links": [
        {"title": "Guide", "url": "getting-started"},
        {"title": "API", "url": "api/index"},
        {"title": "GitHub", "url": "https://github.com/you/your-project", "external": True},
    ],
}
```

### Dropdown Menus

Create dropdown navigation menus with the `children` key:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "nav_links": [
        {
            "title": "Reference",
            "children": [
                {"title": "Typography", "url": "reference/typography"},
                {"title": "Code Blocks", "url": "reference/code-blocks"},
            ],
        },
    ],
}
```

## Social Links

Display icon links in the header (currently supports GitHub):

```{code-block} python
:caption: conf.py
html_theme_options = {
    "social_links": [
        {"icon": "github", "url": "https://github.com/you/your-project"},
    ],
}
```

## Sidebar Depth

Control how deep the sidebar table of contents tree expands:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "nav_depth": "3",   # Default: 3 levels deep
}
```

## Breadcrumbs

The breadcrumb trail above the content helps readers orient themselves. To hide it:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "show_breadcrumbs": "false",
}
```

## Page Table of Contents

The right-side page outline shows h2 and h3 headings. To hide it:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "show_toc": "false",
}
```

## Previous / Next Navigation

Page-level previous/next links appear at the bottom of each page. To hide them:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "show_prev_next": "false",
}
```
