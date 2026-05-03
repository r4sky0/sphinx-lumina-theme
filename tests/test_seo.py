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


def test_should_emit_seo_default_true():
    """No disable_seo key → SEO is emitted."""
    from sphinx_lumina_theme._seo import should_emit_seo

    assert should_emit_seo({}) is True
    assert should_emit_seo({"disable_seo": "false"}) is True


def test_should_emit_seo_disabled():
    """disable_seo=true (case-insensitive) suppresses SEO emission."""
    from sphinx_lumina_theme._seo import should_emit_seo

    assert should_emit_seo({"disable_seo": "true"}) is False
    assert should_emit_seo({"disable_seo": "TRUE"}) is False


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


def test_extract_description_uses_front_matter():
    """Front-matter `description` wins over doctree extraction."""
    from sphinx_lumina_theme._seo import extract_description

    result = extract_description(
        doctree=None,
        meta={"description": "From front matter"},
        short_title="Project",
    )
    assert result == "From front matter"


def test_extract_description_falls_back_to_first_paragraph():
    """Without front matter, use the first prose paragraph."""
    from docutils import frontend, utils
    from docutils.parsers.rst import Parser
    from sphinx_lumina_theme._seo import extract_description

    rst = "Title\n=====\n\nThis is the first paragraph with enough text to qualify as prose.\n"
    parser = Parser()
    settings = frontend.get_default_settings(Parser)
    doc = utils.new_document("<test>", settings)
    parser.parse(rst, doc)

    result = extract_description(doctree=doc, meta={}, short_title="Project")
    assert result is not None
    assert "first paragraph" in result


def test_extract_description_skips_short_paragraphs():
    """Paragraphs under 30 chars don't qualify (avoid taglines)."""
    from docutils import frontend, utils
    from docutils.parsers.rst import Parser
    from sphinx_lumina_theme._seo import extract_description

    rst = (
        "Title\n=====\n\n"
        "Short.\n\n"
        "This second paragraph has enough characters to be a real description.\n"
    )
    parser = Parser()
    settings = frontend.get_default_settings(Parser)
    doc = utils.new_document("<test>", settings)
    parser.parse(rst, doc)

    result = extract_description(doctree=doc, meta={}, short_title="Project")
    assert result is not None
    assert "second paragraph" in result


def test_extract_description_falls_back_to_short_title():
    """When the doctree has no usable paragraph, fall back to short_title."""
    from sphinx_lumina_theme._seo import extract_description

    result = extract_description(doctree=None, meta={}, short_title="My Project")
    assert result == "My Project"


def test_extract_description_returns_none_when_no_source():
    """No front matter, no doctree, no short title → None."""
    from sphinx_lumina_theme._seo import extract_description

    assert extract_description(doctree=None, meta={}, short_title="") is None


def test_extract_description_truncates_to_160_chars():
    """Long paragraphs are truncated cleanly."""
    from docutils import frontend, utils
    from docutils.parsers.rst import Parser
    from sphinx_lumina_theme._seo import extract_description

    long_text = "word " * 200  # > 160 chars
    rst = f"Title\n=====\n\n{long_text}\n"
    parser = Parser()
    settings = frontend.get_default_settings(Parser)
    doc = utils.new_document("<test>", settings)
    parser.parse(rst, doc)

    result = extract_description(doctree=doc, meta={}, short_title="X")
    assert result is not None
    assert len(result) <= 163  # 160 + ellipsis
