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
