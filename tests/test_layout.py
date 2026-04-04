"""Test the three-column layout structure."""


def test_has_three_column_grid(index_html):
    """Layout should have header, sidebar, content, and TOC areas."""
    assert index_html.find(id="lumina-header") is not None, "Missing header"
    assert index_html.find(id="lumina-sidebar") is not None, "Missing sidebar"
    assert index_html.find(id="lumina-content") is not None, "Missing content"
    assert index_html.find(id="lumina-toc") is not None, "Missing TOC"


def test_content_has_pagefind_body(index_html):
    """Content area should have data-pagefind-body for search indexing."""
    content = index_html.find(id="lumina-content")
    assert content is not None
    assert content.get("data-pagefind-body") is not None


def test_dark_mode_script_in_head(index_html):
    """An inline script should set data-theme before paint to prevent flash."""
    head = index_html.find("head")
    scripts = head.find_all("script")
    inline_scripts = [s for s in scripts if s.string and "lumina-theme" in s.string]
    assert len(inline_scripts) > 0, "Missing dark mode pre-paint script in <head>"


def test_external_scripts_are_deferred(index_html):
    """All external scripts should have the defer attribute to avoid render-blocking."""
    head = index_html.find("head")
    for script in head.find_all("script", src=True):
        assert script.get("defer") is not None, (
            f"Script {script['src']} is missing defer attribute"
        )


def test_inline_scripts_not_deferred(index_html):
    """Inline scripts should NOT have defer (it's meaningless for inline)."""
    head = index_html.find("head")
    for script in head.find_all("script"):
        if not script.get("src"):
            assert script.get("defer") is None, "Inline script should not have defer"


def test_lumina_js_is_included(index_html):
    """lumina.js should be included via the script files mechanism."""
    head = index_html.find("head")
    scripts = [s["src"] for s in head.find_all("script", src=True)]
    lumina_scripts = [s for s in scripts if "lumina.js" in s]
    assert len(lumina_scripts) == 1, "lumina.js should appear exactly once"


def test_font_preload(index_html):
    """Primary font should have a preload hint."""
    head = index_html.find("head")
    preloads = head.find_all("link", rel="preload")
    font_preloads = [
        el for el in preloads if "source-sans-3-regular" in el.get("href", "")
    ]
    assert len(font_preloads) == 1, "Missing preload for Source Sans 3 Regular"
    link = font_preloads[0]
    assert link.get("as") == "font"
    assert link.get("crossorigin") is not None, "Font preload must have crossorigin"
