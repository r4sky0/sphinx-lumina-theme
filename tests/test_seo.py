"""Tests for Lumina SEO primitives."""


from bs4 import BeautifulSoup
from conftest import copy_sample_docs
from sphinx.application import Sphinx


def _build(
    tmp_path, *, options=None, baseurl="", confoverrides=None, project="Test Project"
):
    """Build sample docs with custom Lumina options + return the build dir."""
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir(parents=True)
    out_dir = tmp_path / "build"
    doctree_dir = out_dir / ".doctrees"

    opts = options or {}
    conf_lines = [
        f'project = "{project}"',
        'extensions = ["myst_parser"]',
        'html_theme = "lumina"',
        f"html_theme_options = {opts!r}",
    ]
    if baseurl:
        conf_lines.append(f'html_baseurl = "{baseurl}"')
    conf_lines.append('exclude_patterns = ["_build"]')
    (conf_dir / "conf.py").write_text("\n".join(conf_lines) + "\n")

    copy_sample_docs(conf_dir)

    app = Sphinx(
        srcdir=str(conf_dir),
        confdir=str(conf_dir),
        outdir=str(out_dir),
        doctreedir=str(doctree_dir),
        buildername="html",
        freshenv=True,
        confoverrides=confoverrides or {},
    )
    app.build()
    return out_dir


def _soup(out_dir, page="index.html"):
    return BeautifulSoup((out_dir / page).read_text(), "html.parser")


def test_seo_theme_options_accepted(tmp_path):
    """The new SEO theme options should be accepted without error."""
    out = _build(
        tmp_path,
        options={
            "og_image": "card.png",
            "og_image_alt": "Lumina docs",
            "twitter_site": "@example",
            "seo_keywords": "sphinx, theme",
            "disable_seo": "false",
        },
    )
    assert (out / "index.html").exists(), "Build should succeed with new options"
