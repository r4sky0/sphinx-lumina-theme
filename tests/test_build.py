"""Test that the theme builds without errors."""


def test_build_succeeds(build_output):
    """The theme should build sample docs without errors."""
    index = build_output / "index.html"
    assert index.exists(), "index.html was not generated"


def test_static_assets_copied(build_output):
    """Compiled CSS and JS should be copied to the output."""
    static = build_output / "_static"
    assert (static / "lumina.css").exists()
    assert (static / "lumina.js").exists()


def test_all_pages_build(build_output):
    """All sample doc pages should be generated."""
    assert (build_output / "index.html").exists()
    assert (build_output / "getting-started.html").exists()


def test_lumina_css_linked(index_html):
    """lumina.css should be linked in the page."""
    stylesheets = [
        link.get("href", "") for link in index_html.find_all("link", rel="stylesheet")
    ]
    lumina_css = [s for s in stylesheets if "lumina.css" in s]
    assert len(lumina_css) > 0, "lumina.css not linked"
