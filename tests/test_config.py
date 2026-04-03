"""Test theme configuration options."""

import shutil
from pathlib import Path

from bs4 import BeautifulSoup
from sphinx.application import Sphinx


def build_with_options(tmp_path, options):
    """Build sample docs with custom theme options."""
    src_dir = Path(__file__).parent / "sample_docs"
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


def test_custom_accent_color(tmp_path):
    """Custom accent color should appear as CSS variable override."""
    html = build_with_options(tmp_path, {"accent_color": "#8b5cf6"})
    page_text = str(html)
    assert "#8b5cf6" in page_text


def test_hide_toc(tmp_path):
    """Setting show_toc to False should remove the TOC sidebar."""
    html = build_with_options(tmp_path, {"show_toc": "false"})
    toc = html.find(id="lumina-toc")
    assert toc is None


def test_hide_breadcrumbs(tmp_path):
    """Setting show_breadcrumbs to False should remove breadcrumbs."""
    html = build_with_options(tmp_path, {"show_breadcrumbs": "false"})
    breadcrumbs = html.find(attrs={"aria-label": "Breadcrumb"})
    assert breadcrumbs is None
