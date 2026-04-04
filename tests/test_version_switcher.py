"""Test the version switcher dropdown."""

import shutil
from pathlib import Path

from bs4 import BeautifulSoup
from sphinx.application import Sphinx


def _build_with_options(tmp_path, options=None):
    """Build sample docs with custom options and return parsed index HTML."""
    src_dir = Path(__file__).parent / "sample_docs"
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    out_dir = tmp_path / "build"
    doctree_dir = out_dir / ".doctrees"

    opts = options or {}
    (conf_dir / "conf.py").write_text(
        'project = "Test"\n'
        'extensions = ["myst_parser"]\n'
        'html_theme = "lumina"\n'
        f"html_theme_options = {opts!r}\n"
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


def test_no_switcher_by_default(index_html):
    """Version switcher should not render when options are empty."""
    switcher = index_html.find(id="lumina-version-switcher")
    assert switcher is None, "Version switcher should not render without config"


def test_switcher_renders_when_configured(tmp_path):
    """Version switcher should render when json URL and match are set."""
    html = _build_with_options(
        tmp_path,
        {
            "version_switcher_json": "https://example.com/versions.json",
            "version_switcher_match": "1.17",
        },
    )
    switcher = html.find(id="lumina-version-switcher")
    assert switcher is not None, "Version switcher not found"


def test_switcher_has_json_url_data(tmp_path):
    """Switcher element should have the JSON URL as a data attribute."""
    html = _build_with_options(
        tmp_path,
        {
            "version_switcher_json": "https://example.com/versions.json",
            "version_switcher_match": "1.17",
        },
    )
    switcher = html.find(id="lumina-version-switcher")
    assert switcher.get("data-json-url") == "https://example.com/versions.json"


def test_switcher_has_version_match_data(tmp_path):
    """Switcher element should have the version match as a data attribute."""
    html = _build_with_options(
        tmp_path,
        {
            "version_switcher_json": "https://example.com/versions.json",
            "version_switcher_match": "1.17",
        },
    )
    switcher = html.find(id="lumina-version-switcher")
    assert switcher.get("data-version-match") == "1.17"


def test_switcher_not_rendered_without_json(tmp_path):
    """Switcher should not render if only match is set (no JSON URL)."""
    html = _build_with_options(
        tmp_path,
        {
            "version_switcher_match": "1.17",
        },
    )
    switcher = html.find(id="lumina-version-switcher")
    assert switcher is None, "Switcher should not render without JSON URL"


def test_switcher_has_aria_label(tmp_path):
    """Switcher button should have an accessible label."""
    html = _build_with_options(
        tmp_path,
        {
            "version_switcher_json": "https://example.com/versions.json",
            "version_switcher_match": "1.17",
        },
    )
    switcher = html.find(id="lumina-version-switcher")
    button = switcher.find("button")
    assert button is not None, "Switcher should contain a button"
    assert button.get("aria-label") or button.get("aria-haspopup"), (
        "Switcher button should have ARIA attributes"
    )


def test_build_warns_when_json_set_without_match(tmp_path):
    """Build should succeed when json is set but match is empty."""
    src_dir = Path(__file__).parent / "sample_docs"
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    out_dir = tmp_path / "build"
    doctree_dir = out_dir / ".doctrees"

    (conf_dir / "conf.py").write_text(
        'project = "Test"\n'
        'extensions = ["myst_parser"]\n'
        'html_theme = "lumina"\n'
        'html_theme_options = {"version_switcher_json": "https://example.com/versions.json"}\n'
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
    # Build should succeed (warning, not error)
    app.build()

    html = BeautifulSoup((out_dir / "index.html").read_text(), "html.parser")
    switcher = html.find(id="lumina-version-switcher")
    assert switcher is not None, "Switcher should still render even without match"
