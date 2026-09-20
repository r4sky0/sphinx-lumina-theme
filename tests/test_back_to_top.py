"""Test the back-to-top button."""

from bs4 import BeautifulSoup
from conftest import copy_sample_docs, sphinx_app


def _build_with_options(tmp_path, options=None):
    """Build sample docs with custom options and return parsed index HTML."""
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    out_dir = tmp_path / "build"

    opts = options or {}
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
    return BeautifulSoup((out_dir / "index.html").read_text(), "html.parser")


def test_back_to_top_present_by_default(index_html):
    """Back-to-top button should be present with default options."""
    btn = index_html.find(id="lumina-back-to-top")
    assert btn is not None, "Back-to-top button not found"


def test_back_to_top_has_aria_label(index_html):
    """Button should have an accessible label."""
    btn = index_html.find(id="lumina-back-to-top")
    assert btn.get("aria-label") == "Back to top"


def test_back_to_top_hidden_when_disabled(tmp_path):
    """Button should not render when show_back_to_top is false."""
    html = _build_with_options(tmp_path, {"show_back_to_top": "false"})
    btn = html.find(id="lumina-back-to-top")
    assert btn is None, "Button should not render when disabled"


def test_back_to_top_is_button_element(index_html):
    """Back-to-top should be a button element for accessibility."""
    btn = index_html.find(id="lumina-back-to-top")
    assert btn.name == "button", f"Expected button, got {btn.name}"
