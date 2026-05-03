"""SEO primitives for the Lumina theme.

All functions here are pure (no Sphinx app state mutation). They take
the data they need and return strings, dicts, or HTML-ready values to
be injected into the Jinja template context.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

# Public API surface (kept thin and explicit).
__all__ = [
    "should_emit_seo",
]


def should_emit_seo(theme_options: Mapping[str, Any]) -> bool:
    """Return False when the user has disabled all SEO emission."""
    return str(theme_options.get("disable_seo", "false")).lower() != "true"
