"""SEO primitives for the Lumina theme.

All functions here are pure (no Sphinx app state mutation). They take
the data they need and return strings, dicts, or HTML-ready values to
be injected into the Jinja template context.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from docutils import nodes

# Minimum prose length (characters) for a paragraph to be considered a
# valid description fallback. Avoids picking up taglines like "Quick start.".
_MIN_PROSE_LEN = 30

# Hard cap on description length. 160 chars is the de-facto upper bound
# Google uses in SERP snippets; we leave a few chars for the ellipsis.
_MAX_DESC_LEN = 160


__all__ = [
    "extract_description",
    "should_emit_seo",
]


def should_emit_seo(theme_options: Mapping[str, Any]) -> bool:
    """Return False when the user has disabled all SEO emission."""
    return str(theme_options.get("disable_seo", "false")).lower() != "true"


def extract_description(
    doctree: nodes.document | None,
    meta: Mapping[str, Any],
    short_title: str | None,
) -> str | None:
    """Return a meta description for a page, or None if no source qualifies.

    Fallback chain:
      1. ``meta["description"]`` (MyST front matter / RST :description: field).
      2. First paragraph in the doctree containing real prose
         (>= _MIN_PROSE_LEN chars, not inside an admonition / code / toctree).
      3. ``short_title`` (typically Sphinx's html_short_title).
      4. None.
    """
    fm = meta.get("description")
    if fm:
        return _truncate(str(fm).strip())

    paragraph = _first_prose_paragraph(doctree) if doctree is not None else None
    if paragraph:
        return _truncate(paragraph)

    if short_title:
        return _truncate(str(short_title).strip())

    return None


def _truncate(text: str) -> str:
    text = " ".join(text.split())  # collapse whitespace
    if len(text) <= _MAX_DESC_LEN:
        return text
    return text[: _MAX_DESC_LEN - 1].rstrip() + "…"


def _first_prose_paragraph(doctree: nodes.document) -> str | None:
    """Walk the doctree, return the first paragraph node that qualifies."""
    from docutils import nodes

    try:
        from sphinx import addnodes
    except ImportError:  # tests using a bare docutils doctree
        addnodes = None

    skip_ancestors: tuple[type, ...] = (
        nodes.literal_block,
        nodes.admonition,
        nodes.note,
        nodes.warning,
        nodes.tip,
        nodes.important,
        nodes.caution,
        nodes.attention,
        nodes.hint,
        nodes.danger,
        nodes.error,
        nodes.comment,
        nodes.system_message,
        nodes.field_list,
        nodes.docinfo,
    )
    if addnodes is not None:
        skip_ancestors = skip_ancestors + (addnodes.toctree,)

    for para in doctree.findall(nodes.paragraph):
        ancestor = para.parent
        skip = False
        while ancestor is not None:
            if isinstance(ancestor, skip_ancestors):
                skip = True
                break
            ancestor = ancestor.parent
        if skip:
            continue
        text = para.astext().strip()
        if len(text) >= _MIN_PROSE_LEN:
            return text
    return None
