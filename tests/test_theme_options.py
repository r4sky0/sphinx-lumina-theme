"""Test theme option rendering."""

from conftest import sphinx_app
from bs4 import BeautifulSoup


def test_nav_links_render(index_html):
    """Header should contain configured nav link items."""
    nav = index_html.find("nav", attrs={"aria-label": "Top navigation"})
    assert nav is not None, "Missing top navigation nav element"
    links = nav.find_all("a")
    link_texts = [a.get_text(strip=True) for a in links]
    assert "Guide" in link_texts


def test_social_links_render(index_html):
    """Header should contain social link icons."""
    social = index_html.find("a", attrs={"aria-label": lambda v: v and "Github" in v})
    assert social is not None, "Missing GitHub social link"
    assert social.get("target") == "_blank"


def test_edit_on_github_link(index_html):
    """TOC sidebar should have an 'Edit this page' link with correct URL."""
    edit_link = None
    for a in index_html.find_all("a"):
        if "Edit" in a.get_text():
            edit_link = a
            break
    assert edit_link is not None, "Missing edit link"
    href = edit_link.get("href", "")
    assert "github.com/example/test" in href


def test_default_options(tmp_path):
    """Build with no custom theme options should succeed with defaults."""
    conf_dir = tmp_path / "src"
    conf_dir.mkdir()
    out_dir = tmp_path / "build"

    (conf_dir / "conf.py").write_text(
        'project = "Defaults Test"\n'
        'extensions = ["myst_parser"]\n'
        'html_theme = "lumina"\n'
        'exclude_patterns = ["_build"]\n'
    )
    (conf_dir / "index.md").write_text("# Hello\n\nMinimal page.\n")

    app = sphinx_app(conf_dir, out_dir)
    app.build()
    html = BeautifulSoup((out_dir / "index.html").read_text(), "html.parser")

    assert html.find("header") is not None
    assert html.find(class_="lumina-sidebar-nav") is not None


def test_code_wrap_toggle_is_opt_in(tmp_path):
    """The wrap-long-lines toggle is off unless code_wrap_toggle is "true"."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "conf.py").write_text('project = "Wrap"\nhtml_theme = "lumina"\n')
    (src / "index.rst").write_text("Wrap\n====\n\n::\n\n    code\n")

    sphinx_app(src, tmp_path / "default").build()
    assert "dataset.codeWrap" not in (tmp_path / "default/index.html").read_text()

    sphinx_app(
        src,
        tmp_path / "enabled",
        confoverrides={"html_theme_options.code_wrap_toggle": "true"},
    ).build()
    assert "dataset.codeWrap" in (tmp_path / "enabled/index.html").read_text()
