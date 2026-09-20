"""Tests for the auto-generated JavaScript API documentation page."""

from conftest import sphinx_app
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

DOCS_DIR = Path(__file__).parent.parent / "docs"

# All exported Alpine.js component functions that should appear on the page
EXPECTED_FUNCTIONS = [
    "boot",
    "scrollspy",
    "sidebar",
    "navDropdown",
    "versionSwitcher",
    "themeToggle",
    "searchModal",
    "backToTop",
    "announcementBanner",
    "headerLinks",
    "copyPage",
    "curlCopyBtn",
    "curlCopy",
    "tryItPanel",
    "tryIt",
]


@pytest.fixture(scope="module")
def docs_build(tmp_path_factory):
    """Build the full documentation site and return the output path."""
    out_dir = tmp_path_factory.mktemp("docs_build")

    app = sphinx_app(DOCS_DIR, out_dir)
    app.build()
    return out_dir


@pytest.fixture(scope="module")
def js_api_html(docs_build):
    """Return parsed HTML of the JavaScript API page."""
    html_path = docs_build / "contributing" / "javascript-api.html"
    assert html_path.exists(), "javascript-api.html was not generated"
    return BeautifulSoup(html_path.read_text(), "html.parser")


def test_js_api_page_exists(docs_build):
    """The JavaScript API page should be generated."""
    assert (docs_build / "contributing" / "javascript-api.html").exists()


def test_js_api_page_title(js_api_html):
    """The page should have the correct title."""
    h1 = js_api_html.find("h1")
    assert h1 is not None
    assert "JavaScript API" in h1.get_text()


def test_all_functions_documented(js_api_html):
    """Every exported function should appear as a documented entry."""
    sig_elements = js_api_html.find_all("dt", class_="sig")
    documented_names = [dt.get_text(strip=True).rstrip("¶") for dt in sig_elements]

    for func_name in EXPECTED_FUNCTIONS:
        match = any(func_name in name for name in documented_names)
        assert match, (
            f"Function '{func_name}' not found in documented signatures: {documented_names}"
        )


def test_functions_have_descriptions(js_api_html):
    """Each documented function should have a non-empty description."""
    dl_entries = js_api_html.find_all("dl", class_="js")
    assert len(dl_entries) >= len(EXPECTED_FUNCTIONS)

    for dl in dl_entries:
        dd = dl.find("dd")
        assert dd is not None, f"Missing description block in {dl}"
        text = dd.get_text(strip=True)
        assert len(text) > 10, f"Description too short or empty: '{text[:50]}'"


def test_section_headings_present(js_api_html):
    """The page should have logical grouping headings."""
    headings = [h.get_text(strip=True).rstrip("¶") for h in js_api_html.find_all("h2")]
    expected_sections = [
        "Entry Point",
        "Navigation",
        "UI Controls",
        "Content Utilities",
        "API Tools",
    ]
    for section in expected_sections:
        assert section in headings, (
            f"Section heading '{section}' not found in {headings}"
        )


def test_architecture_cross_reference(docs_build):
    """The architecture page should link to the JS API page."""
    arch_path = docs_build / "contributing" / "architecture.html"
    assert arch_path.exists()
    soup = BeautifulSoup(arch_path.read_text(), "html.parser")
    links = [a.get("href", "") for a in soup.find_all("a")]
    assert any("javascript-api" in href for href in links), (
        "architecture.html should link to javascript-api"
    )


def test_contributing_index_has_js_api_card(docs_build):
    """The contributing index should have a card linking to the JS API page."""
    index_path = docs_build / "contributing" / "index.html"
    assert index_path.exists()
    soup = BeautifulSoup(index_path.read_text(), "html.parser")
    text = soup.get_text()
    assert "JavaScript API" in text, "Contributing index should mention JavaScript API"
    links = [a.get("href", "") for a in soup.find_all("a")]
    assert any("javascript-api" in href for href in links), (
        "Contributing index should link to javascript-api"
    )


def test_page_uses_lumina_theme(js_api_html):
    """The page should be rendered with the Lumina theme."""
    stylesheets = [
        link.get("href", "") for link in js_api_html.find_all("link", rel="stylesheet")
    ]
    assert any("lumina.css" in s for s in stylesheets), "Page should use lumina.css"
