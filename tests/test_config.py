"""Test theme configuration options."""

from bs4 import BeautifulSoup
from conftest import copy_sample_docs
from sphinx.application import Sphinx


def build_with_options(tmp_path, options):
    """Build sample docs with custom theme options."""
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    out_dir = tmp_path / "build"
    doctree_dir = out_dir / ".doctrees"

    conf_py = conf_dir / "conf.py"
    conf_py.write_text(
        f'project = "Test"\n'
        f'extensions = ["myst_parser"]\n'
        f'html_theme = "lumina"\n'
        f"html_theme_options = {options!r}\n"
        f'exclude_patterns = ["_build"]\n'
    )

    copy_sample_docs(conf_dir)

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


def test_custom_accent_color(tmp_path):
    """Custom accent color should appear as CSS variable override."""
    html = build_with_options(tmp_path, {"accent_color": "#8b5cf6"})
    page_text = str(html)
    assert "#8b5cf6" in page_text
    assert "--lumina-link:color-mix(in srgb,#8b5cf6" in page_text


def test_hide_toc(tmp_path):
    """Setting show_toc to False should remove the TOC sidebar."""
    html = build_with_options(tmp_path, {"show_toc": "false"})
    toc = html.find(id="lumina-toc")
    assert toc is None
    assert html.find(class_="lumina-mobile-outline") is None


def test_page_actions_respect_options(tmp_path):
    html = build_with_options(tmp_path, {"show_reading_time": "false"})
    actions = html.find(class_="lumina-page-actions")
    assert actions is not None
    assert actions.find("button", attrs={"aria-label": "Copy page as Markdown"})
    assert html.find(class_="lumina-reading-time") is None
    assert actions.find("a") is None  # No repository configured.


def test_hide_breadcrumbs(tmp_path):
    """Setting show_breadcrumbs to False should remove breadcrumbs."""
    html = build_with_options(tmp_path, {"show_breadcrumbs": "false"})
    breadcrumbs = html.find(attrs={"aria-label": "Breadcrumb"})
    assert breadcrumbs is None


def test_reading_time_below_introduction(tmp_path):
    html = build_with_options(tmp_path, {"show_reading_time": "true"})
    metadata = html.select_one(".lumina-article h1 + p + .lumina-reading-time")
    assert metadata is not None
    assert metadata.has_attr("data-pagefind-ignore")
    assert metadata.select_one('svg[aria-hidden="true"]') is not None
    assert "min read" in metadata.get_text()
    assert html.select_one(".lumina-page-actions .lumina-reading-time") is None
