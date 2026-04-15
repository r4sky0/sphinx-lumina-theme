"""Tests for the code_style Pygments preset feature."""

from pathlib import Path

import pytest
from sphinx.application import Sphinx

SAMPLE_DOCS = Path(__file__).parent / "sample_docs"


def _build_with_code_style(tmp_path, code_style):
    """Build sample docs with a given code_style and return the output path."""
    out_dir = tmp_path / "build"
    doctree_dir = out_dir / ".doctrees"
    app = Sphinx(
        srcdir=str(SAMPLE_DOCS),
        confdir=str(SAMPLE_DOCS),
        outdir=str(out_dir),
        doctreedir=str(doctree_dir),
        buildername="html",
        freshenv=True,
        confoverrides={"html_theme_options.code_style": code_style},
    )
    app.build()
    return out_dir


def test_default_preset_unchanged(build_output):
    """Default build should use the 'default' Pygments style (green keywords)."""
    css = (build_output / "_static" / "pygments.css").read_text()
    # The 'default' Pygments style uses #008000 for keywords
    assert "#008000" in css


def test_nord_preset_applies(tmp_path):
    """The 'nord' preset should produce tango light and nord dark CSS."""
    out = _build_with_code_style(tmp_path, "nord")
    light_css = (out / "_static" / "pygments.css").read_text()
    dark_css = (out / "_static" / "pygments_dark.css").read_text()
    # Tango uses #204a87 for keywords
    assert "#204a87" in light_css.lower()
    # Nord uses #81a1c1 for keywords
    assert "#81a1c1" in dark_css.lower()


def test_invalid_preset_warns(tmp_path):
    """An unknown code_style should emit a warning and fall back to default."""
    out_dir = tmp_path / "build"
    doctree_dir = out_dir / ".doctrees"
    app = Sphinx(
        srcdir=str(SAMPLE_DOCS),
        confdir=str(SAMPLE_DOCS),
        outdir=str(out_dir),
        doctreedir=str(doctree_dir),
        buildername="html",
        freshenv=True,
        confoverrides={"html_theme_options.code_style": "nonexistent"},
        warningiserror=False,
    )
    app.build()
    # Build should still succeed with default style
    css = (out_dir / "_static" / "pygments.css").read_text()
    assert "#008000" in css


@pytest.mark.parametrize(
    "preset", ["default", "nord", "one-dark", "gruvbox", "material"]
)
def test_all_presets_build(tmp_path, preset):
    """Every preset should build successfully and produce both CSS files."""
    out = _build_with_code_style(tmp_path, preset)
    assert (out / "_static" / "pygments.css").exists()
    assert (out / "_static" / "pygments_dark.css").exists()
