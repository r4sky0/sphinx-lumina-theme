"""Test header nav dropdown rendering."""

import shutil
from pathlib import Path

from bs4 import BeautifulSoup
from sphinx.application import Sphinx
import pytest


@pytest.fixture(scope="module")
def dropdown_html(tmp_path_factory):
    """Build sample docs with dropdown nav links and return parsed HTML."""
    tmp_path = tmp_path_factory.mktemp("dropdown")
    src_dir = Path(__file__).parent / "sample_docs"
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    out_dir = tmp_path / "build"
    doctree_dir = out_dir / ".doctrees"

    conf_py = conf_dir / "conf.py"
    conf_py.write_text(
        'project = "Test"\n'
        'extensions = ["myst_parser"]\n'
        'html_theme = "lumina"\n'
        "html_theme_options = {\n"
        '    "nav_links": [\n'
        '        {"title": "Guide", "url": "getting-started"},\n'
        '        {"title": "Reference", "children": [\n'
        '            {"title": "API", "url": "getting-started"},\n'
        '            {"title": "CLI", "url": "getting-started"},\n'
        "        ]},\n"
        "    ],\n"
        "}\n"
        'exclude_patterns = ["_build"]\n'
    )

    for f in src_dir.iterdir():
        if f.name != "conf.py":
            shutil.copy2(f, conf_dir / f.name)

    app = Sphinx(
        srcdir=str(conf_dir),
        confdir=str(conf_dir),
        outdir=str(out_dir),
        doctreedir=str(doctree_dir),
        buildername="html",
        freshenv=True,
    )
    app.build()
    return BeautifulSoup((out_dir / "index.html").read_text(), "html.parser")


def test_flat_nav_link_renders(dropdown_html):
    """Flat nav links should render as plain anchor tags."""
    nav = dropdown_html.find("nav", attrs={"aria-label": "Top navigation"})
    assert nav is not None, "Top navigation not found"
    guide_link = nav.find("a", string="Guide")
    assert guide_link is not None, "Flat nav link 'Guide' not found"


def test_dropdown_trigger_renders(dropdown_html):
    """Dropdown nav links should render a trigger button."""
    nav = dropdown_html.find("nav", attrs={"aria-label": "Top navigation"})
    assert "Reference" in nav.get_text(), "Dropdown trigger 'Reference' not found"


def test_dropdown_children_render(dropdown_html):
    """Dropdown nav links should render child items."""
    nav = dropdown_html.find("nav", attrs={"aria-label": "Top navigation"})
    text = nav.get_text()
    assert "API" in text, "Dropdown child 'API' not found"
    assert "CLI" in text, "Dropdown child 'CLI' not found"


def test_dropdown_has_aria_attributes(dropdown_html):
    """Dropdown should have proper ARIA attributes."""
    nav = dropdown_html.find("nav", attrs={"aria-label": "Top navigation"})
    trigger = nav.find(attrs={"aria-haspopup": "true"})
    assert trigger is not None, "Dropdown trigger missing aria-haspopup"


def test_mobile_sidebar_has_dropdown_items(dropdown_html):
    """Mobile sidebar should include flattened dropdown items."""
    sidebar_drawer = dropdown_html.find(id="lumina-sidebar-drawer")
    assert sidebar_drawer is not None, "Mobile sidebar drawer not found"
    # The drawer lives inside a <template x-teleport>, so get_text() is
    # empty in BeautifulSoup.  Instead, search for child <a> elements.
    links = [a.string for a in sidebar_drawer.find_all("a") if a.string]
    assert "API" in links, "Mobile sidebar missing dropdown child 'API'"
    assert "CLI" in links, "Mobile sidebar missing dropdown child 'CLI'"
