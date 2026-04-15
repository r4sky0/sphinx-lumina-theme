"""Utility functions for rendering Lucide icons as inline SVG."""

from urllib.parse import quote

from markupsafe import Markup


def get_icon_svg(name, size=24, css_class="", stroke_width=2):
    """Return inline SVG markup for a Lucide icon name.

    Returns empty string if the icon name is not found.
    """
    from ._icons import ICONS

    inner = ICONS.get(name)
    if not inner:
        return ""

    cls = f' class="{css_class}"' if css_class else ""
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="{stroke_width}" stroke-linecap="round" '
        f'stroke-linejoin="round"{cls} aria-hidden="true">'
        f"{inner}</svg>"
    )
    return Markup(svg)


def get_icon_inner(name):
    """Return just the inner SVG paths for a Lucide icon (no <svg> wrapper).

    Useful when the <svg> element is defined in the template (e.g. with
    Alpine.js directives) and only the inner paths are needed.
    """
    from ._icons import ICONS

    return Markup(ICONS.get(name, ""))


def get_icon_data_href(name, stroke="currentColor", stroke_width=2):
    """Return a bare ``data:image/svg+xml,...`` URI for a Lucide icon.

    Suitable for use as an ``href`` on ``<link rel="icon">``. Unlike
    :func:`get_icon_data_uri`, no ``url("...")`` wrapping is applied, and
    the stroke color can be customized (favicons render outside any CSS
    context, so ``currentColor`` is not resolvable).
    """
    from ._icons import ICONS

    inner = ICONS.get(name)
    if not inner:
        return ""

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        f'fill="none" stroke="{stroke}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )
    return f"data:image/svg+xml,{quote(svg, safe='/:@!$&()*+,;=')}"


def get_icon_data_uri(name, stroke_width=2):
    """Return a CSS-ready data URI for a Lucide icon.

    Suitable for use in mask-image or background-image CSS properties.
    """
    href = get_icon_data_href(name, stroke_width=stroke_width)
    return f'url("{href}")' if href else ""
