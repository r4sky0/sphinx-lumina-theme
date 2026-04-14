"""Tests for the Lucide icon system."""

import pytest
from bs4 import BeautifulSoup

from sphinx_lumina_theme._icon_utils import get_icon_svg


class TestGetIconSvg:
    """Tests for the get_icon_svg() render function."""

    def test_valid_icon_returns_svg(self):
        result = get_icon_svg("rocket")
        assert result.startswith("<svg ")
        assert 'aria-hidden="true"' in result
        assert "</svg>" in result

    def test_invalid_icon_returns_empty(self):
        result = get_icon_svg("nonexistent-icon-xyz")
        assert result == ""

    def test_custom_size(self):
        result = get_icon_svg("rocket", size=16)
        assert 'width="16"' in result
        assert 'height="16"' in result

    def test_default_size_is_24(self):
        result = get_icon_svg("rocket")
        assert 'width="24"' in result
        assert 'height="24"' in result

    def test_css_class(self):
        result = get_icon_svg("rocket", css_class="lumina-icon")
        assert 'class="lumina-icon"' in result

    def test_no_class_when_empty(self):
        result = get_icon_svg("rocket")
        assert "class=" not in result

    def test_stroke_attributes(self):
        result = get_icon_svg("rocket")
        assert 'stroke="currentColor"' in result
        assert 'stroke-linecap="round"' in result
        assert 'stroke-linejoin="round"' in result
        assert 'fill="none"' in result

    def test_custom_stroke_width(self):
        result = get_icon_svg("rocket", stroke_width=1.5)
        assert 'stroke-width="1.5"' in result

    def test_viewbox_always_24(self):
        """ViewBox is always 0 0 24 24 regardless of size param."""
        result = get_icon_svg("rocket", size=16)
        assert 'viewBox="0 0 24 24"' in result


@pytest.fixture(scope="module")
def icons_html(build_output):
    """Return parsed HTML of the icons test page."""
    html_path = build_output / "icons-test.html"
    return BeautifulSoup(html_path.read_text(), "html.parser")


class TestCardIcons:
    """Tests for icon rendering on sphinx-design cards."""

    def test_inline_icon_card_has_svg(self, icons_html):
        """Card with :icon: should contain an SVG with lumina-icon class."""
        cards = icons_html.find_all("div", class_="sd-card")
        inline_card = cards[0]
        svg = inline_card.find("svg", class_="lumina-icon")
        assert svg is not None, (
            "Inline icon card should have an SVG with class lumina-icon"
        )

    def test_inline_icon_wrapper_class(self, icons_html):
        """Inline icon style should have the sd-card-icon-inline wrapper."""
        cards = icons_html.find_all("div", class_="sd-card")
        inline_card = cards[0]
        wrapper = inline_card.find(class_="sd-card-icon-inline")
        assert wrapper is not None

    def test_featured_icon_card_has_pill(self, icons_html):
        """Featured icon style should have the sd-card-icon-featured wrapper."""
        cards = icons_html.find_all("div", class_="sd-card")
        featured_card = cards[1]
        pill = featured_card.find(class_="sd-card-icon-featured")
        assert pill is not None

    def test_no_icon_card_unchanged(self, icons_html):
        """Card without :icon: should not have any icon markup."""
        cards = icons_html.find_all("div", class_="sd-card")
        plain_card = cards[2]
        assert plain_card.find("svg", class_="lumina-icon") is None

    def test_grid_item_card_icon(self, icons_html):
        """grid-item-card with :icon: should render the icon."""
        cards = icons_html.find_all("div", class_="sd-card")
        grid_card = cards[3]
        svg = grid_card.find("svg", class_="lumina-icon")
        assert svg is not None


class TestSidebarIcons:
    """Tests for icon rendering in sidebar navigation."""

    def test_page_with_icon_has_svg_in_sidebar(self, icons_html):
        """Page with icon frontmatter should have SVG in its sidebar link.

        On the icons-test page itself, its own sidebar link has href="#"
        (self-reference). The sidebar filter should still inject the icon.
        """
        sidebar = icons_html.find("nav", class_="lumina-sidebar-nav")
        assert sidebar is not None, "Sidebar nav should exist"
        # The current page link uses href="#" in the sidebar
        link = sidebar.find("a", href="#")
        assert link is not None, "Should find current page link (#) in sidebar"
        svg = link.find("svg", class_="lumina-sidebar-icon")
        assert svg is not None, "Sidebar link for icons-test should have an icon SVG"

    def test_page_without_icon_has_no_svg(self, icons_html):
        """Page without icon frontmatter should not have SVG in sidebar."""
        sidebar = icons_html.find("nav", class_="lumina-sidebar-nav")
        assert sidebar is not None
        link = sidebar.find("a", href=lambda h: h and "getting-started" in h)
        assert link is not None, "Should find getting-started link in sidebar"
        svg = link.find("svg", class_="lumina-sidebar-icon")
        assert svg is None, "Sidebar link without icon metadata should have no icon"


class TestLogoIcon:
    """Tests for the logo_icon theme option."""

    def test_logo_icon_renders_svg_in_header(self, icons_html):
        """When logo_icon is set, header should contain an SVG with lumina-logo-icon class."""
        header = icons_html.find("header")
        assert header is not None
        svg = header.find("svg", class_="lumina-logo-icon")
        assert svg is not None, "Header should have a logo icon SVG"

    def test_logo_icon_has_aria_hidden(self, icons_html):
        """Logo icon SVG should be decorative (aria-hidden)."""
        header = icons_html.find("header")
        svg = header.find("svg", class_="lumina-logo-icon")
        assert svg is not None
        assert svg.get("aria-hidden") == "true"
