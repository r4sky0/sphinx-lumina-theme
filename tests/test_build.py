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


def test_wide_layout_has_fouc_script(wide_build_output):
    """Wide layout build should include FOUC prevention script."""
    html = (wide_build_output / "index.html").read_text()
    assert "lumina-layout" in html
    assert "data-layout" in html


def test_wide_layout_has_toggle_button(wide_build_output):
    """Wide layout build should include the layout toggle button."""
    from bs4 import BeautifulSoup

    html = (wide_build_output / "getting-started.html").read_text()
    soup = BeautifulSoup(html, "html.parser")
    toggle = soup.find("button", attrs={"x-data": "layoutToggle()"})
    assert toggle is not None, "Layout toggle button not found"


def test_default_layout_no_wide_features(index_html):
    """Default build should not include wide layout toggle or FOUC script."""
    # No layout toggle button
    toggle = index_html.find("button", attrs={"x-data": "layoutToggle()"})
    assert toggle is None, "Layout toggle should not be present in default build"


def test_always_wide_has_fouc_script(always_wide_build_output):
    """Always-wide build should unconditionally set data-layout in FOUC script."""
    html = (always_wide_build_output / "index.html").read_text()
    assert "data-layout" in html
    # Should NOT check localStorage — it's always wide
    assert "lumina-layout" not in html


def test_always_wide_no_toggle_button(always_wide_build_output):
    """Always-wide build should not include the layout toggle button."""
    from bs4 import BeautifulSoup

    html = (always_wide_build_output / "getting-started.html").read_text()
    soup = BeautifulSoup(html, "html.parser")
    toggle = soup.find("button", attrs={"x-data": "layoutToggle()"})
    assert toggle is None, "Layout toggle should not be present in always-wide build"


def _has_breadcrumbs(build_output, page):
    return 'aria-label="Breadcrumb"' in (build_output / page).read_text()


def test_breadcrumbs_hidden_on_root_page(build_output):
    """The root page's trail would only repeat its own title, so it is omitted."""
    assert not _has_breadcrumbs(build_output, "index.html")
    assert _has_breadcrumbs(build_output, "getting-started.html")


def test_breadcrumbs_hidden_by_front_matter(build_output):
    """`hide_breadcrumbs: true` front matter removes the trail from one page."""
    assert not _has_breadcrumbs(build_output, "intro.html")
