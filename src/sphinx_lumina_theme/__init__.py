"""Sphinx Lumina Theme — a modern documentation theme."""

import copy
import hashlib
import re
from pathlib import Path

from sphinx import addnodes
from sphinx.environment.adapters.toctree import _resolve_toctree
from sphinx.util import logging

logger = logging.getLogger(__name__)

__version__ = "1.28.0"

_HERO_FIELDS = (
    "hero_title",
    "hero_subtitle",
    "hero_primary_url",
    "hero_primary_text",
    "hero_secondary_url",
    "hero_secondary_text",
    "hero_tags",
)


def _build_page_icons(app):
    """Build a mapping of pagename → icon name from page metadata."""
    icons = {}
    for pagename, meta in app.env.metadata.items():
        icon = meta.get("icon", "")
        if icon:
            icons[pagename] = icon
    return icons


def _add_sidebar_icons(toctree_html, page_icons, pagename, get_icon_fn):
    """Post-process toctree HTML to inject icon SVGs into sidebar links."""
    if not page_icons:
        return toctree_html

    def _replace_link(match):
        full_match = match.group(0)
        href = match.group(1)
        # Self-reference links (current page) use href="#"
        if href == "#" or href == "":
            icon_name = page_icons.get(pagename, "")
        else:
            # Resolve href to pagename: strip .html, handle relative paths
            target = re.sub(r"\.html$", "", href)
            target = re.sub(r"/$", "/index", target)
            # Handle relative URLs by resolving against current page
            if not target.startswith("/") and "/" in pagename:
                base = pagename.rsplit("/", 1)[0]
                target = base + "/" + target
            # Also try without path prefix for top-level pages
            icon_name = page_icons.get(target, "")
            if not icon_name:
                # Try stripping leading segments
                simple = target.rsplit("/", 1)[-1] if "/" in target else target
                icon_name = page_icons.get(simple, "")
        if not icon_name:
            return full_match
        svg = get_icon_fn(icon_name, size=16, css_class="lumina-sidebar-icon")
        if not svg:
            return full_match
        # Insert SVG right after the opening <a ...> tag
        return full_match + str(svg)

    return re.sub(r'<a\b[^>]*href="([^"]*)"[^>]*>', _replace_link, toctree_html)


def _section_paths(section):
    """Return the list of path prefixes for a section.

    Supports both ``"path": "guides"`` (single) and
    ``"paths": ["getting-started", "guides"]`` (multiple).
    """
    paths = list(section.get("paths") or [])
    single = section.get("path", "")
    if single and single not in paths:
        paths.insert(0, single)
    return paths


def _paths_to_docnames(path_list):
    """Expand path prefixes to the set of docnames they match in root toctree."""
    result = set()
    for p in path_list:
        result.add(p)
        result.add(p + "/index")
    return result


def _detect_section(pagename, sections):
    """Return the section config dict matching pagename by path prefix.

    If a section has ``"default": True``, it matches any page not claimed
    by another section's explicit paths.
    """
    default = None
    for section in sections:
        if section.get("default"):
            default = section
            continue
        for prefix in _section_paths(section):
            if (
                pagename == prefix
                or pagename == prefix + "/index"
                or pagename.startswith(prefix + "/")
            ):
                return section
    return default


def _prepare_sections(app, sections):
    """Pre-compute cached data for doc sections (called once per build).

    Enriches each section dict with ``_link`` (nav target) and stores
    the root doctree and claimed-paths set on the app for reuse across pages.
    """
    root_doc = app.env.config.root_doc

    # Compute link targets and the set of all explicitly claimed docnames
    claimed = set()
    for s in sections:
        # Explicit "link" takes priority, then first path, then root_doc
        if "link" in s:
            s["_link"] = s["link"]
        else:
            paths = _section_paths(s)
            if paths:
                s["_link"] = paths[0] + "/index"
            else:
                s["_link"] = root_doc
        if not s.get("default"):
            claimed |= _paths_to_docnames(_section_paths(s))

    # Cache the root doctree (constant during write phase)
    try:
        app._lumina_root_doctree = app.env.get_doctree(root_doc)
    except FileNotFoundError:
        app._lumina_root_doctree = None

    app._lumina_claimed_paths = claimed


def _section_toctree(app, pagename, section, maxdepth, collapse):
    """Render toctree HTML for a section's subtree(s).

    Resolves the **root** document's toctree but filters its entries to only
    include those matching the section's path prefixes.  For a default section,
    includes all entries not claimed by any other section.

    Note: ``_resolve_toctree`` is a private API but has been stable across
    Sphinx 7.x and 8.x.  This project requires ``sphinx>=8.0``.
    """
    root_doctree = app._lumina_root_doctree
    if root_doctree is None:
        return ""

    is_default = section.get("default", False)
    if is_default:
        claimed = app._lumina_claimed_paths
    else:
        claimed = _paths_to_docnames(_section_paths(section))

    builder = app.builder
    fragments = []
    for node in root_doctree.findall(addnodes.toctree):
        if is_default:
            matching = [e for e in node["entries"] if e[1] not in claimed]
        else:
            matching = [e for e in node["entries"] if e[1] in claimed]
        if not matching:
            continue

        filtered = copy.deepcopy(node)
        filtered["entries"] = matching
        matched_docs = {dn for _, dn in matching}
        filtered["includefiles"] = [
            f for f in node["includefiles"] if f in matched_docs
        ]

        resolved = _resolve_toctree(
            app.env,
            pagename,
            builder,
            filtered,
            prune=True,
            maxdepth=maxdepth,
            titles_only=True,
            collapse=collapse,
            includehidden=True,
            tags=builder.tags,
        )
        if resolved:
            fragments.append(builder.render_partial(resolved)["fragment"])

    return "\n".join(fragments)


def _add_context(app, pagename, templatename, context, doctree):
    context["lumina_version"] = __version__
    context["has_llms_txt"] = "sphinx_llm.txt" in app.extensions
    wide_val = app.builder.theme_options.get("wide_layout", "false")
    context["lumina_wide_layout"] = wide_val is True or str(wide_val).lower() == "true"

    # Separate light/dark logos
    light_logo = app.builder.theme_options.get("light_logo", "")
    dark_logo = app.builder.theme_options.get("dark_logo", "")

    if light_logo:
        context["lumina_light_logo"] = context["pathto"]("_static/" + light_logo, 1)
    if dark_logo:
        context["lumina_dark_logo"] = context["pathto"]("_static/" + dark_logo, 1)

    # Announcement banner
    announcement = app.builder.theme_options.get("announcement", "")
    if announcement:
        context["announcement_content"] = announcement
        context["announcement_id"] = hashlib.md5(
            announcement.encode(), usedforsecurity=False
        ).hexdigest()[:8]

    # Version switcher
    vs_json = app.builder.theme_options.get("version_switcher_json", "")
    vs_match = app.builder.theme_options.get("version_switcher_match", "")
    if vs_json:
        context["lumina_version_json"] = vs_json
        context["lumina_version_match"] = vs_match
        if not vs_match:
            logger.warning(
                "version_switcher_json is set but version_switcher_match is empty — "
                "the version dropdown will not highlight the current version"
            )

    # Allow pages to opt into a custom template via metadata
    meta = app.env.metadata.get(pagename, {})

    # Pass hero metadata fields to the template context
    for field in _HERO_FIELDS:
        if field in meta:
            context[field] = meta[field]

    # Icon system: make icon renderer and sidebar filter available to templates
    from ._icon_utils import get_icon_inner, get_icon_svg

    context["lumina_icon"] = get_icon_svg
    context["lumina_icon_inner"] = get_icon_inner

    page_icons = _build_page_icons(app)
    context["add_sidebar_icons"] = lambda html: _add_sidebar_icons(
        html, page_icons, pagename, get_icon_svg
    )

    # Doc sections switcher
    sections = app.builder.theme_options.get("doc_sections", "")
    if sections:
        if not hasattr(app, "_lumina_root_doctree"):
            _prepare_sections(app, sections)
        current_section = _detect_section(pagename, sections)
        context["lumina_sections"] = sections
        context["lumina_current_section"] = current_section
        if current_section:
            maxdepth = int(app.builder.theme_options.get("nav_depth", "3"))
            section_html = _section_toctree(
                app, pagename, current_section, maxdepth, collapse=False
            )
            if section_html:
                context["lumina_section_toctree"] = section_html

    # Make all external scripts non-render-blocking (defer).
    # Sphinx places the {%- block scripts %} inside <head>, so without defer
    # every script blocks rendering.  We wrap the built-in js_tag() function
    # to inject defer="defer" into all external <script> tags while leaving
    # inline scripts (FOUC prevention, announcement state) synchronous.
    _original_js_tag = context["js_tag"]

    def _deferred_js_tag(js):
        tag = _original_js_tag(js)
        if "src=" in tag and "defer" not in tag and "async" not in tag:
            tag = tag.replace("<script ", '<script defer="defer" ', 1)
        return tag

    context["js_tag"] = _deferred_js_tag

    if "template" in meta:
        # Icon browser page: inject all icon names + SVG inner content
        if meta["template"] == "icon-browser.html":
            from ._icons import ICONS

            context["icon_entries"] = sorted(ICONS.items())
            context["icon_count"] = len(ICONS)
        return meta["template"]


def _run_pagefind(app, exception):
    """Run Pagefind to index the built HTML for search."""
    if exception:
        return
    if app.builder.format != "html":
        return
    if app.builder.theme_options.get("search_backend", "pagefind") != "pagefind":
        return

    import shutil
    import subprocess

    npx = shutil.which("npx")
    if not npx:
        logger.warning(
            "npx not found — skipping Pagefind indexing. "
            "Install Node.js or run manually: npx pagefind --site %s",
            app.outdir,
        )
        return

    logger.info("Running Pagefind indexing...")
    try:
        subprocess.run(
            [
                npx,
                "pagefind",
                "--site",
                app.outdir,
                "--output-subdir",
                "_pagefind",
                # Sphinx injects ¶ anchor links into headings — exclude them so they
                # don't corrupt page titles and result excerpts in the search index.
                "--exclude-selectors",
                "a.headerlink",
                # HTTP domain signature lines contain bare method verbs (GET, POST …)
                # which cause false positives via stemming (e.g. "Getting" → "get").
                # The endpoint descriptions (inside dd) are still fully indexed.
                "--exclude-selectors",
                "dl.http dt.sig",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("Pagefind index created successfully")
    except subprocess.CalledProcessError as e:
        logger.warning("Pagefind indexing failed: %s", e.stderr.strip())
    except FileNotFoundError:
        logger.warning("Pagefind not found — skipping search indexing")


def setup(app):
    """Register the Lumina theme with Sphinx."""
    from ._directives import LuminaCardDirective, LuminaGridItemCardDirective

    app.add_html_theme("lumina", str(Path(__file__).parent / "theme"))
    app.add_js_file("lumina.js", loading_method="defer", priority=900)
    app.add_directive("card", LuminaCardDirective, override=True)
    app.add_directive("grid-item-card", LuminaGridItemCardDirective, override=True)
    app.connect("html-page-context", _add_context)
    app.connect("build-finished", _run_pagefind)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
