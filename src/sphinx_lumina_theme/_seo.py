"""SEO primitives for the Lumina theme.

All functions here are pure (no Sphinx app state mutation). They take
the data they need and return strings, dicts, or HTML-ready values to
be injected into the Jinja template context.
"""

from __future__ import annotations

import json as _json
import posixpath as _posixpath
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
    "build_article_jsonld",
    "build_breadcrumb_jsonld",
    "build_website_jsonld",
    "derive_twitter_handle",
    "extract_description",
    "og_locale_for_language",
    "resolve_og_image",
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


# Common Sphinx language code → OG-locale mapping. We keep this small
# and let unknown short codes fall back to "<code>_<CODE>" (e.g. "de" → "de_DE").
_OG_LOCALE_OVERRIDES = {
    "en": "en_US",
    "zh-cn": "zh_CN",
    "zh-tw": "zh_TW",
    "pt-br": "pt_BR",
}


def og_locale_for_language(language: str | None) -> str:
    """Map a Sphinx ``language`` config value to an Open Graph locale string."""
    if not language:
        return "en_US"
    code = language.lower()
    if code in _OG_LOCALE_OVERRIDES:
        return _OG_LOCALE_OVERRIDES[code]
    if "-" in code:
        lang, region = code.split("-", 1)
        return f"{lang}_{region.upper()}"
    if "_" in code:
        lang, region = code.split("_", 1)
        return f"{lang}_{region.upper()}"
    return f"{code}_{code.upper()}"


_RASTER_EXTS = (".png", ".jpg", ".jpeg", ".webp")


def resolve_og_image(
    *,
    page_meta: Mapping[str, Any],
    theme_options: Mapping[str, Any],
    html_logo: str | None,
    html_baseurl: str | None,
) -> tuple[str | None, str | None]:
    """Return (og_image_url, og_image_alt) using the documented fallback chain.

    Fallback chain:
      1. page front-matter `og_image`
      2. theme option `og_image`
      3. `html_logo` (if a raster format)
      4. None

    Relative values are resolved as paths under ``_static/`` and joined to
    ``html_baseurl`` when set, so the emitted tag is an absolute URL.
    """
    page_image = str(page_meta.get("og_image", "")).strip()
    theme_image = str(theme_options.get("og_image", "")).strip()
    alt = (
        str(page_meta.get("og_image_alt", "")).strip()
        or str(theme_options.get("og_image_alt", "")).strip()
    )

    candidate = page_image or theme_image
    if not candidate and html_logo:
        if html_logo.lower().endswith(_RASTER_EXTS):
            candidate = html_logo

    if not candidate:
        return None, None

    if candidate.startswith(("http://", "https://", "//")):
        return candidate, alt or None

    # Treat anything else as a static-asset filename.
    rel = candidate.lstrip("/")
    if not rel.startswith("_static/"):
        rel = f"_static/{rel}"

    if html_baseurl:
        base = html_baseurl.rstrip("/") + "/"
        return _posixpath.join(base, rel), alt or None

    # No base URL — emit a relative URL. Social platforms generally need
    # an absolute URL, but a relative one is better than nothing for local
    # previews and won't produce a "broken image" upstream.
    return rel, alt or None


def derive_twitter_handle(theme_options: Mapping[str, Any]) -> str | None:
    """Return a Twitter/X handle (with leading @) or None.

    Looks at ``twitter_site`` first, then any Twitter/X entry in
    ``social_links`` (icon == "twitter" or "x").
    """
    explicit = str(theme_options.get("twitter_site", "")).strip()
    if explicit:
        return explicit if explicit.startswith("@") else f"@{explicit}"

    social = theme_options.get("social_links") or []
    if not isinstance(social, list):
        return None
    for entry in social:
        if not isinstance(entry, dict):
            continue
        icon = str(entry.get("icon", "")).strip().lower()
        if icon not in ("twitter", "x"):
            continue
        url = str(entry.get("url", "")).strip()
        handle = _handle_from_twitter_url(url)
        if handle:
            return handle
    return None


def _handle_from_twitter_url(url: str) -> str | None:
    """Extract @handle from a Twitter/X profile URL like https://twitter.com/foo."""
    if not url:
        return None
    for prefix in (
        "https://twitter.com/",
        "https://www.twitter.com/",
        "https://x.com/",
        "https://www.x.com/",
    ):
        if url.startswith(prefix):
            tail = url[len(prefix) :].strip("/").split("/", 1)[0]
            if tail:
                return f"@{tail}"
    return None


def build_breadcrumb_jsonld(
    *,
    parents,
    title: str,
    page_url: str,
    site_url: str,
    site_name: str,
) -> str | None:
    """Build a BreadcrumbList JSON-LD string. Returns None when the page is the root.

    ``parents`` follows Sphinx's html-page-context format: a list of dicts with
    ``title`` and ``link`` keys, in order from root to direct parent.
    """
    if not parents and not title:
        return None

    items = []
    pos = 1
    if site_url:
        items.append(
            {
                "@type": "ListItem",
                "position": pos,
                "name": site_name,
                "item": site_url.rstrip("/") + "/",
            }
        )
        pos += 1

    for parent in parents or []:
        items.append(
            {
                "@type": "ListItem",
                "position": pos,
                "name": parent.get("title", ""),
                "item": _absolute_url(parent.get("link", ""), site_url),
            }
        )
        pos += 1

    items.append(
        {
            "@type": "ListItem",
            "position": pos,
            "name": title,
            "item": page_url or _absolute_url("", site_url),
        }
    )

    return _json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items,
        },
        ensure_ascii=False,
    )


def _absolute_url(relative: str, site_url: str) -> str:
    """Make a best-effort absolute URL from a Sphinx-relative link."""
    if not relative:
        return site_url.rstrip("/") + "/"
    if relative.startswith(("http://", "https://", "//")):
        return relative
    if not site_url:
        return relative
    return site_url.rstrip("/") + "/" + relative.lstrip("/")


def build_article_jsonld(
    *,
    headline: str,
    description: str | None,
    page_url: str,
    site_url: str,
    site_name: str,
    author: str | None,
    image_url: str | None,
    date_published: str | None = None,
    date_modified: str | None = None,
) -> str:
    """Build a TechArticle JSON-LD string. Caller decides whether to emit."""
    publisher: dict[str, Any] = {"@type": "Organization", "name": site_name}
    if image_url:
        publisher["logo"] = {"@type": "ImageObject", "url": image_url}

    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": headline,
        "author": {"@type": "Person", "name": author or site_name},
        "publisher": publisher,
    }
    if description:
        data["description"] = description
    if page_url:
        data["url"] = page_url
        data["mainEntityOfPage"] = page_url
    if image_url:
        data["image"] = image_url
    if date_published:
        data["datePublished"] = date_published
    if date_modified:
        data["dateModified"] = date_modified

    return _json.dumps(data, ensure_ascii=False)


def build_website_jsonld(
    *,
    site_url: str,
    site_name: str,
    description: str | None = None,
) -> str | None:
    """Build a WebSite JSON-LD string with a SearchAction.

    Returns None when ``site_url`` is empty (a relative WebSite URL is invalid).
    The SearchAction points at the on-site search page; Lumina's search modal
    accepts ``?q=`` so the SearchAction template lines up.
    """
    if not site_url:
        return None
    base = site_url.rstrip("/") + "/"
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site_name,
        "url": base,
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{base}search.html?q={{search_term_string}}",
            },
            "query-input": "required name=search_term_string",
        },
    }
    if description:
        data["description"] = description
    return _json.dumps(data, ensure_ascii=False)
