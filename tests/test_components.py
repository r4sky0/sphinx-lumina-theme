"""Test that theme components render correctly."""


def test_header_contains_project_name(index_html):
    """Header should display the project name."""
    header = index_html.find(id="lumina-header")
    assert "Test Project" in header.get_text()


def test_header_has_search_trigger(index_html):
    """Header should have a search button."""
    header = index_html.find(id="lumina-header")
    search_btn = header.find(attrs={"data-search-trigger": True})
    assert search_btn is not None, "Missing search trigger button"


def test_header_has_theme_toggle(index_html):
    """Header should have a dark mode toggle button."""
    header = index_html.find(id="lumina-header")
    toggle = header.find(attrs={"data-theme-toggle": True})
    assert toggle is not None, "Missing theme toggle button"


def test_sidebar_has_navigation(index_html):
    """Sidebar should contain navigation from toctree."""
    sidebar = index_html.find(id="lumina-sidebar")
    nav = sidebar.find("nav")
    assert nav is not None, "Missing nav element in sidebar"


def test_sidebar_has_aria_label(index_html):
    """Sidebar nav should have accessible label."""
    sidebar = index_html.find(id="lumina-sidebar")
    nav = sidebar.find("nav", attrs={"aria-label": True})
    assert nav is not None, "Missing aria-label on sidebar nav"


def test_toc_has_page_headings(index_html):
    """Right TOC should contain links to page sections."""
    toc = index_html.find(id="lumina-toc")
    links = toc.find_all("a")
    texts = [a.get_text(strip=True) for a in links]
    assert "Section One" in texts
    assert "Section Two" in texts
