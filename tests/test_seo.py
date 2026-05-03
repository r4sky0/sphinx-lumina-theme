"""Tests for Lumina SEO primitives."""

import json

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
    assert len(result) <= 160
    assert result.endswith("…")


def test_meta_description_from_front_matter(tmp_path):
    """When a page sets `description` in front matter, it appears as <meta>."""
    out = _build(tmp_path)
    soup = _soup(out, "seo-described.html")
    tag = soup.find("meta", attrs={"name": "description"})
    assert tag is not None
    assert tag["content"] == "Custom description for the SEO sample page"


def test_meta_description_falls_back_to_paragraph(tmp_path):
    """When a page has no front-matter description, derive from first paragraph."""
    out = _build(tmp_path)
    soup = _soup(out, "index.html")
    tag = soup.find("meta", attrs={"name": "description"})
    assert tag is not None
    assert (
        "test document" in tag["content"].lower() or "welcome" in tag["content"].lower()
    )


def test_meta_theme_color_from_accent(tmp_path):
    """theme-color reflects the accent_color theme option."""
    out = _build(tmp_path, options={"accent_color": "#ff00aa"})
    soup = _soup(out, "index.html")
    tag = soup.find("meta", attrs={"name": "theme-color"})
    assert tag is not None
    assert tag["content"] == "#ff00aa"


def test_canonical_link_when_baseurl_set(tmp_path):
    """When html_baseurl is set, every page emits a canonical link."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "index.html")
    canonical = soup.find("link", attrs={"rel": "canonical"})
    assert canonical is not None
    assert canonical["href"] == "https://example.com/index.html"


def test_canonical_link_absent_when_baseurl_unset(tmp_path):
    """Without html_baseurl, no canonical tag is emitted."""
    out = _build(tmp_path, baseurl="")
    soup = _soup(out, "index.html")
    canonical = soup.find("link", attrs={"rel": "canonical"})
    assert canonical is None


def test_og_tags_basic(tmp_path):
    """Index page emits og:title, og:description, og:url, og:type, og:site_name."""
    out = _build(tmp_path, baseurl="https://example.com/", project="My Site")
    soup = _soup(out, "index.html")

    def og(prop):
        tag = soup.find("meta", attrs={"property": f"og:{prop}"})
        return tag["content"] if tag else None

    assert og("title")
    assert og("description")
    assert og("url") == "https://example.com/index.html"
    assert og("type") == "website"  # root page
    assert og("site_name") == "My Site"
    assert og("locale") == "en_US"


def test_og_type_article_for_content_pages(tmp_path):
    """Non-root pages get og:type=article."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "seo-described.html")
    tag = soup.find("meta", attrs={"property": "og:type"})
    assert tag is not None
    assert tag["content"] == "article"


def test_og_locale_from_language_config(tmp_path):
    """og:locale comes from Sphinx language config."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        confoverrides={"language": "de"},
    )
    soup = _soup(out, "index.html")
    tag = soup.find("meta", attrs={"property": "og:locale"})
    assert tag is not None
    assert tag["content"] == "de_DE"


def test_disable_seo_suppresses_everything(tmp_path):
    """disable_seo=true emits no description, theme-color, canonical, or OG tags."""
    out = _build(
        tmp_path,
        options={"disable_seo": "true"},
        baseurl="https://example.com/",
    )
    soup = _soup(out, "index.html")

    assert soup.find("meta", attrs={"name": "description"}) is None
    assert soup.find("meta", attrs={"name": "theme-color"}) is None
    assert soup.find("link", attrs={"rel": "canonical"}) is None
    assert soup.find("meta", attrs={"property": "og:title"}) is None
    assert soup.find("meta", attrs={"property": "og:type"}) is None


def test_seo_enabled_by_default(tmp_path):
    """When disable_seo is unset, OG tags are emitted."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "index.html")
    assert soup.find("meta", attrs={"property": "og:title"}) is not None


def test_keywords_from_theme_option(tmp_path):
    """seo_keywords theme option is rendered as <meta name=keywords>."""
    out = _build(tmp_path, options={"seo_keywords": "sphinx, theme, dark mode"})
    soup = _soup(out, "index.html")
    tag = soup.find("meta", attrs={"name": "keywords"})
    assert tag is not None
    assert tag["content"] == "sphinx, theme, dark mode"


def test_keywords_from_front_matter_overrides(tmp_path):
    """Page front-matter `keywords` overrides the sitewide option."""
    out = _build(tmp_path, options={"seo_keywords": "sitewide"})
    soup = _soup(out, "seo-keywords.html")
    tag = soup.find("meta", attrs={"name": "keywords"})
    assert tag is not None
    assert tag["content"] == "page-specific, terms"


def test_keywords_absent_when_unset(tmp_path):
    """No keywords are emitted when neither option nor front matter sets them."""
    out = _build(tmp_path)
    soup = _soup(out, "index.html")
    assert soup.find("meta", attrs={"name": "keywords"}) is None


def test_og_image_from_theme_option(tmp_path):
    """og_image theme option becomes og:image (resolved as static asset)."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        options={"og_image": "card.png", "og_image_alt": "Site card"},
    )
    soup = _soup(out, "index.html")
    img = soup.find("meta", attrs={"property": "og:image"})
    assert img is not None
    # Static asset resolves to absolute URL when html_baseurl is set.
    assert img["content"] == "https://example.com/_static/card.png"
    alt = soup.find("meta", attrs={"property": "og:image:alt"})
    assert alt is not None
    assert alt["content"] == "Site card"


def test_og_image_absolute_url_passes_through(tmp_path):
    """An absolute og_image URL is used verbatim."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        options={"og_image": "https://cdn.example.com/card.png"},
    )
    soup = _soup(out, "index.html")
    img = soup.find("meta", attrs={"property": "og:image"})
    assert img["content"] == "https://cdn.example.com/card.png"


def test_og_image_per_page_override(tmp_path):
    """Per-page front-matter og_image overrides the sitewide default."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        options={"og_image": "default.png"},
    )
    soup = _soup(out, "seo-image-override.html")
    img = soup.find("meta", attrs={"property": "og:image"})
    assert img["content"].endswith("/_static/page-card.png")


def test_og_image_absent_when_no_source(tmp_path):
    """No og_image set, no html_logo set → no og:image emitted."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "index.html")
    assert soup.find("meta", attrs={"property": "og:image"}) is None


def test_twitter_card_summary_large_image_with_image(tmp_path):
    """When og:image is present, Twitter card uses summary_large_image."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        options={"og_image": "card.png", "twitter_site": "@example"},
    )
    soup = _soup(out, "index.html")

    def tw(name):
        tag = soup.find("meta", attrs={"name": f"twitter:{name}"})
        return tag["content"] if tag else None

    assert tw("card") == "summary_large_image"
    assert tw("title")
    assert tw("description")
    assert tw("image")
    assert tw("site") == "@example"


def test_twitter_card_summary_without_image(tmp_path):
    """No image → Twitter card downgrades to summary."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "index.html")
    tag = soup.find("meta", attrs={"name": "twitter:card"})
    assert tag is not None
    assert tag["content"] == "summary"
    assert soup.find("meta", attrs={"name": "twitter:image"}) is None


def test_twitter_site_from_social_links(tmp_path):
    """Twitter handle falls back to social_links Twitter entry."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        options={
            "social_links": [
                {"icon": "twitter", "url": "https://twitter.com/luminadocs"},
            ],
        },
    )
    soup = _soup(out, "index.html")
    tag = soup.find("meta", attrs={"name": "twitter:site"})
    assert tag is not None
    assert tag["content"] == "@luminadocs"


def _ld_blocks(soup):
    """Return list of parsed JSON-LD blocks on the page."""
    blocks = []
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            blocks.append(json.loads(tag.string or ""))
        except json.JSONDecodeError:
            pass
    return blocks


def _block_of_type(blocks, schema_type):
    return next((b for b in blocks if b.get("@type") == schema_type), None)


def test_breadcrumb_jsonld_on_nested_page(tmp_path):
    """A non-root page emits BreadcrumbList JSON-LD with the page chain."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "seo-described.html")
    blocks = _ld_blocks(soup)
    crumbs = _block_of_type(blocks, "BreadcrumbList")
    assert crumbs is not None
    assert crumbs["@context"] == "https://schema.org"
    items = crumbs["itemListElement"]
    assert len(items) >= 2  # home + current page
    assert items[0]["position"] == 1
    assert items[-1]["name"]  # current page has a name
    for item in items:
        assert item["@type"] == "ListItem"


def test_breadcrumb_jsonld_absent_on_root(tmp_path):
    """The root document does NOT emit BreadcrumbList (it has no breadcrumb)."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "index.html")
    blocks = _ld_blocks(soup)
    assert _block_of_type(blocks, "BreadcrumbList") is None
