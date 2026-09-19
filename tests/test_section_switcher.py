"""Test the doc sections switcher."""

from bs4 import BeautifulSoup
from conftest import copy_sample_docs, sphinx_app


def _build_sections(tmp_path, options=None, extra_opts=None):
    """Build sample docs with doc_sections and return output path."""
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    out_dir = tmp_path / "build"

    sections = options or [
        {
            "path": "guides",
            "name": "Guides",
            "description": "How-to walkthroughs",
            "icon": "book-open",
            "color": "#8b5cf6",
        },
    ]

    opts = {"doc_sections": sections}
    if extra_opts:
        opts.update(extra_opts)

    (conf_dir / "conf.py").write_text(
        'project = "Test"\n'
        'extensions = ["myst_parser"]\n'
        'html_theme = "lumina"\n'
        f"html_theme_options = {opts!r}\n"
        'exclude_patterns = ["_build"]\n'
    )

    copy_sample_docs(conf_dir)

    app = sphinx_app(conf_dir, out_dir)
    app.build()
    return out_dir


def _parse(out_dir, page="index.html"):
    return BeautifulSoup((out_dir / page).read_text(), "html.parser")


def test_no_switcher_by_default(index_html):
    """Section switcher should not render when doc_sections is empty."""
    switcher = index_html.find(id="lumina-section-switcher")
    assert switcher is None, "Section switcher should not render without config"


def test_switcher_renders_when_configured(tmp_path):
    """Section switcher should render when doc_sections is set."""
    out = _build_sections(tmp_path)
    html = _parse(out)
    switcher = html.find(id="lumina-section-switcher")
    assert switcher is not None, "Section switcher not found"


def test_switcher_shows_section_name(tmp_path):
    """Switcher should display the configured section name."""
    out = _build_sections(tmp_path)
    html = _parse(out, "guides/index.html")
    switcher = html.find(id="lumina-section-switcher")
    name = switcher.find(class_="lumina-section-switcher-name")
    assert name is not None
    assert "Guides" in name.get_text()


def test_switcher_shows_description(tmp_path):
    """Switcher should display the configured section description."""
    out = _build_sections(tmp_path)
    html = _parse(out, "guides/index.html")
    switcher = html.find(id="lumina-section-switcher")
    desc = switcher.find(class_="lumina-section-switcher-desc")
    assert desc is not None
    assert "How-to walkthroughs" in desc.get_text()


def test_switcher_has_section_links(tmp_path):
    """Dropdown should contain links to section index pages."""
    out = _build_sections(tmp_path)
    html = _parse(out)
    switcher = html.find(id="lumina-section-switcher")
    items = switcher.find_all(class_="lumina-section-switcher-item")
    assert len(items) >= 1
    hrefs = [a.get("href", "") for a in items]
    assert any("guides" in h for h in hrefs), f"No guides link found in {hrefs}"


def test_filtered_toctree_on_section_page(tmp_path):
    """Sidebar on a section page should only contain that section's pages."""
    out = _build_sections(tmp_path)
    html = _parse(out, "guides/search.html")
    sidebar = html.find(class_="lumina-sidebar-desktop")
    nav = sidebar.find("nav")
    assert nav is not None
    # Should contain the guides section pages
    nav_text = nav.get_text()
    assert "Search Guide" in nav_text or "search" in str(nav).lower()
    # Should NOT contain top-level pages from outside the section
    assert "Getting Started" not in nav_text or "Welcome" not in nav_text


def test_full_toctree_on_non_section_page(tmp_path):
    """Sidebar on a non-section page should show the full toctree."""
    out = _build_sections(tmp_path)
    html = _parse(out)
    sidebar = html.find(class_="lumina-sidebar-desktop")
    nav = sidebar.find("nav")
    assert nav is not None
    nav_text = nav.get_text()
    # Non-section page should have the full toctree
    assert "Getting Started" in nav_text or "getting-started" in str(nav).lower()


def test_current_class_on_active_page(tmp_path):
    """The active page should have the 'current' class in the sidebar."""
    out = _build_sections(tmp_path)
    html = _parse(out, "guides/search.html")
    sidebar = html.find(class_="lumina-sidebar-desktop")
    nav = sidebar.find("nav")
    current = nav.find(class_="current")
    assert current is not None, "No element with 'current' class found"


def test_switcher_has_aria_attributes(tmp_path):
    """Switcher trigger should have proper ARIA attributes."""
    out = _build_sections(tmp_path)
    html = _parse(out, "guides/index.html")
    switcher = html.find(id="lumina-section-switcher")
    button = switcher.find("button")
    assert button is not None, "Switcher should contain a trigger button"
    assert button.get("aria-haspopup") == "true"
    assert button.get("aria-label") is not None


def test_active_section_highlighted(tmp_path):
    """Current section item in dropdown should have the active class."""
    out = _build_sections(tmp_path)
    html = _parse(out, "guides/index.html")
    switcher = html.find(id="lumina-section-switcher")
    active = switcher.find(class_="active")
    assert active is not None, "No active section item found"


def test_browse_sections_on_root_page(tmp_path):
    """Root page should show 'Browse sections' when not in any section."""
    out = _build_sections(tmp_path)
    html = _parse(out)
    switcher = html.find(id="lumina-section-switcher")
    trigger = switcher.find("button")
    assert "Browse sections" in trigger.get_text()


def test_section_color_in_styles(tmp_path):
    """Section items should have inline color styles."""
    out = _build_sections(tmp_path)
    html = _parse(out, "guides/index.html")
    switcher = html.find(id="lumina-section-switcher")
    icon = switcher.find(class_="lumina-section-switcher-icon")
    style = icon.get("style", "")
    assert "#8b5cf6" in style, f"Section color not found in style: {style}"
