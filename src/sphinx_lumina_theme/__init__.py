"""Sphinx Lumina Theme — a modern documentation theme."""

from pathlib import Path

from sphinx.util import logging

logger = logging.getLogger(__name__)

__version__ = "1.18.0"

_HERO_FIELDS = (
    "hero_title",
    "hero_subtitle",
    "hero_primary_url",
    "hero_primary_text",
    "hero_secondary_url",
    "hero_secondary_text",
    "hero_tags",
)


def _add_context(app, pagename, templatename, context, doctree):
    context["lumina_version"] = __version__
    context["has_llms_txt"] = "sphinx_llm.txt" in app.extensions
    # Allow pages to opt into a custom template via metadata
    meta = app.env.metadata.get(pagename, {})

    # Pass hero metadata fields to the template context
    for field in _HERO_FIELDS:
        if field in meta:
            context[field] = meta[field]

    if "template" in meta:
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
    app.add_html_theme("lumina", str(Path(__file__).parent / "theme"))
    app.connect("html-page-context", _add_context)
    app.connect("build-finished", _run_pagefind)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
