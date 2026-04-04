"""Test the announcement banner."""

import shutil
from pathlib import Path

from bs4 import BeautifulSoup
from sphinx.application import Sphinx


def _build_with_announcement(tmp_path, announcement="", extra_options=None):
    """Build sample docs with an announcement and return parsed index HTML."""
    src_dir = Path(__file__).parent / "sample_docs"
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir(parents=True)
    out_dir = tmp_path / "build"
    doctree_dir = out_dir / ".doctrees"

    options = {"announcement": announcement}
    if extra_options:
        options.update(extra_options)

    (conf_dir / "conf.py").write_text(
        'project = "Test"\n'
        'extensions = ["myst_parser"]\n'
        'html_theme = "lumina"\n'
        f"html_theme_options = {options!r}\n"
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


def test_announcement_renders_when_set(tmp_path):
    """Banner should appear when announcement option is set."""
    html = _build_with_announcement(tmp_path, announcement="We released v2.0!")
    banner = html.find(id="lumina-announcement")
    assert banner is not None, "Announcement banner not found"
    assert "We released v2.0!" in banner.get_text()


def test_announcement_hidden_when_empty(tmp_path):
    """Banner should not appear when announcement is empty."""
    html = _build_with_announcement(tmp_path, announcement="")
    banner = html.find(id="lumina-announcement")
    assert banner is None, "Banner should not render when announcement is empty"


def test_announcement_has_dismiss_button(tmp_path):
    """Banner should include a dismiss button."""
    html = _build_with_announcement(tmp_path, announcement="Notice!")
    banner = html.find(id="lumina-announcement")
    dismiss_btn = banner.find("button", attrs={"aria-label": "Dismiss announcement"})
    assert dismiss_btn is not None, "Missing dismiss button"


def test_announcement_has_data_id(tmp_path):
    """Banner should include a data-announcement-id for localStorage key."""
    html = _build_with_announcement(tmp_path, announcement="Notice!")
    banner = html.find(id="lumina-announcement")
    assert banner.get("data-announcement-id"), "Missing data-announcement-id attribute"


def test_announcement_id_is_stable(tmp_path):
    """Same announcement content should produce the same ID across builds."""
    html1 = _build_with_announcement(tmp_path / "a", announcement="Same content")
    html2 = _build_with_announcement(tmp_path / "b", announcement="Same content")
    id1 = html1.find(id="lumina-announcement").get("data-announcement-id")
    id2 = html2.find(id="lumina-announcement").get("data-announcement-id")
    assert id1 == id2, "Announcement ID should be stable for same content"


def test_announcement_id_changes_with_content(tmp_path):
    """Different content should produce different IDs."""
    html1 = _build_with_announcement(tmp_path / "a", announcement="Content A")
    html2 = _build_with_announcement(tmp_path / "b", announcement="Content B")
    id1 = html1.find(id="lumina-announcement").get("data-announcement-id")
    id2 = html2.find(id="lumina-announcement").get("data-announcement-id")
    assert id1 != id2, "Different content should produce different IDs"


def test_announcement_renders_html(tmp_path):
    """Banner should render HTML content, not escape it."""
    html = _build_with_announcement(
        tmp_path, announcement='Check the <a href="/changelog">changelog</a>!'
    )
    banner = html.find(id="lumina-announcement")
    link = banner.find("a", href="/changelog")
    assert link is not None, "HTML in announcement should be rendered, not escaped"
