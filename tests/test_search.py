"""Test search modal markup."""


def test_search_modal_exists(index_html):
    """Page should have a search modal element."""
    modal = index_html.find(id="lumina-search-modal")
    assert modal is not None


def test_search_modal_has_input(index_html):
    """Search modal should have an input field."""
    modal = index_html.find(id="lumina-search-modal")
    search_input = modal.find("input", attrs={"type": "search"})
    assert search_input is not None, "Missing search input in modal"


def test_search_base_url_meta_tag(index_html):
    """Page should have a lumina-base-url meta tag for search path resolution."""
    meta = index_html.find("meta", attrs={"name": "lumina-base-url"})
    assert meta is not None, "Missing lumina-base-url meta tag"
    assert meta.get("content"), "lumina-base-url meta tag should have content"


def test_search_metadata_and_heading_anchors(build_output):
    """Index real navigation labels and keep existing section links intact."""
    from bs4 import BeautifulSoup

    html = BeautifulSoup(
        (build_output / "guides/search.html").read_text(), "html.parser"
    )
    assert (
        html.select_one('[data-pagefind-filter="section[content]"]')["content"]
        == "Guides"
    )
    assert (
        html.select_one('[data-pagefind-meta="breadcrumb[content]"]')["content"]
        == "Guides"
    )
    html = BeautifulSoup((build_output / "index.html").read_text(), "html.parser")
    headings = html.select("article section[id] > h2")
    assert headings
    for heading in headings:
        assert heading["id"].startswith("lumina-search-")
        assert heading.select_one("a.headerlink")["href"] == "#" + heading.parent["id"]
    ids = [element["id"] for element in html.select("[id]")]
    assert len(ids) == len(set(ids))


def test_search_sections_follow_toctree_order():
    """Nested/shared documents belong to their first branch; cycles terminate."""
    from types import SimpleNamespace

    from docutils import nodes

    from sphinx_lumina_theme import _prepare_search_sections

    app = SimpleNamespace()
    env = SimpleNamespace(
        config=SimpleNamespace(root_doc="home"),
        titles={
            name: nodes.title(text=title)
            for name, title in [("a", "Guides"), ("b", "API")]
        },
        toctree_includes={
            "home": ["a", "b"],
            "a": ["nested"],
            "nested": ["shared", "home"],
            "b": ["shared", "api"],
        },
    )
    _prepare_search_sections(app, env)
    assert app._lumina_search_sections == {
        "a": "Guides",
        "nested": "Guides",
        "shared": "Guides",
        "b": "API",
        "api": "API",
    }
    env.toctree_includes = {}
    _prepare_search_sections(app, env)
    assert app._lumina_search_sections == {}


def test_search_configured_sections(tmp_path):
    """Search shares the navigation switcher's default and multi-path rules."""
    from bs4 import BeautifulSoup
    from conftest import SAMPLE_DOCS, sphinx_app

    sections = [
        {"name": 'Guides & "Help"', "paths": ["guides", "section"]},
        {"name": "Other docs", "default": True},
    ]
    app = sphinx_app(
        SAMPLE_DOCS,
        tmp_path,
        confoverrides={"html_theme_options.doc_sections": sections},
    )
    app.build()
    for page, expected in [
        ("guides/search", 'Guides & "Help"'),
        ("section/page", 'Guides & "Help"'),
        ("index", "Other docs"),
    ]:
        html = BeautifulSoup((tmp_path / f"{page}.html").read_text(), "html.parser")
        assert (
            html.select_one('[data-pagefind-filter="section[content]"]')["content"]
            == expected
        )


def test_search_heading_alias_collision():
    from types import SimpleNamespace

    from docutils import nodes

    from sphinx_lumina_theme import _add_search_heading_ids

    tree = nodes.document("", "")
    section = nodes.section(ids=["example"])
    title = nodes.title(text="Example")
    section += title
    section += nodes.target(ids=["lumina-search-example"])
    tree += section
    _add_search_heading_ids(
        SimpleNamespace(builder=SimpleNamespace(format="html")), tree, "index"
    )
    assert section["ids"] == ["example"]
    assert title["ids"] == ["lumina-search-example-"]
