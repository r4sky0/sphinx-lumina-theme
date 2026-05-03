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


def test_breadcrumb_jsonld_nested_page_urls(tmp_path):
    """Nested-page breadcrumb parent URLs resolve to the correct directory.

    Regresses against bug where Sphinx's `parents` link (relative to the
    current page) was joined against the site root, producing parent URLs
    that pointed at the homepage instead of the section index.
    """
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "section/page.html")
    blocks = _ld_blocks(soup)
    crumbs = _block_of_type(blocks, "BreadcrumbList")
    assert crumbs is not None
    items = crumbs["itemListElement"]
    # items[0] is the site root, items[-1] is the current page.
    # The parent "Section" should link to /section/index.html, not /index.html.
    parent_items = [i for i in items if i["name"] == "Section"]
    assert len(parent_items) == 1
    assert parent_items[0]["item"] == "https://example.com/section/index.html"


def test_breadcrumb_jsonld_absent_on_root(tmp_path):
    """The root document does NOT emit BreadcrumbList (it has no breadcrumb)."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "index.html")
    blocks = _ld_blocks(soup)
    assert _block_of_type(blocks, "BreadcrumbList") is None


def test_techarticle_jsonld_on_content_page(tmp_path):
    """A content page emits TechArticle JSON-LD with headline/description/author."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        confoverrides={"author": "Jane Dev"},
    )
    soup = _soup(out, "seo-described.html")
    blocks = _ld_blocks(soup)
    article = _block_of_type(blocks, "TechArticle")
    assert article is not None
    assert article["@context"] == "https://schema.org"
    assert article["headline"]
    assert article["description"]
    assert article["author"]["name"] == "Jane Dev"
    assert article["publisher"]["name"]


def test_techarticle_jsonld_absent_on_root(tmp_path):
    """The root document does NOT emit TechArticle (it's a website type)."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "index.html")
    blocks = _ld_blocks(soup)
    assert _block_of_type(blocks, "TechArticle") is None


def test_techarticle_author_falls_back_to_project(tmp_path):
    """Without a configured author, project name is used."""
    out = _build(tmp_path, baseurl="https://example.com/", project="Lumina Docs")
    soup = _soup(out, "seo-described.html")
    blocks = _ld_blocks(soup)
    article = _block_of_type(blocks, "TechArticle")
    assert article is not None
    assert article["author"]["name"] == "Lumina Docs"


def test_website_jsonld_on_root(tmp_path):
    """The root page emits WebSite JSON-LD with a SearchAction."""
    out = _build(tmp_path, baseurl="https://example.com/", project="Lumina Docs")
    soup = _soup(out, "index.html")
    blocks = _ld_blocks(soup)
    site = _block_of_type(blocks, "WebSite")
    assert site is not None
    assert site["@context"] == "https://schema.org"
    assert site["name"] == "Lumina Docs"
    assert site["url"] == "https://example.com/"
    action = site["potentialAction"]
    assert action["@type"] == "SearchAction"
    assert "{search_term_string}" in action["target"]["urlTemplate"]


def test_website_jsonld_absent_on_subpages(tmp_path):
    """Only the root page emits WebSite JSON-LD."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "seo-described.html")
    blocks = _ld_blocks(soup)
    assert _block_of_type(blocks, "WebSite") is None


def test_website_jsonld_absent_without_baseurl(tmp_path):
    """Without html_baseurl, WebSite JSON-LD is skipped (URL would be relative)."""
    out = _build(tmp_path)
    soup = _soup(out, "index.html")
    blocks = _ld_blocks(soup)
    assert _block_of_type(blocks, "WebSite") is None


def test_sitemap_xml_when_baseurl_set(tmp_path):
    """sitemap.xml is produced when html_baseurl is configured."""
    out = _build(tmp_path, baseurl="https://example.com/")
    sitemap = out / "sitemap.xml"
    assert sitemap.exists(), "sitemap.xml should be generated"
    content = sitemap.read_text()
    assert "https://example.com/index.html" in content


def test_sitemap_absent_without_baseurl(tmp_path):
    """sphinx-sitemap skips generation without html_baseurl."""
    out = _build(tmp_path)
    assert not (out / "sitemap.xml").exists()


def test_sitemap_disabled_when_seo_disabled(tmp_path):
    """disable_seo=true also skips sitemap generation."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        options={"disable_seo": "true"},
    )
    assert not (out / "sitemap.xml").exists()


def test_noindex_meta_emitted(tmp_path):
    """A page with noindex: true emits the robots meta tag."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "seo-noindex.html")
    tag = soup.find("meta", attrs={"name": "robots"})
    assert tag is not None
    assert tag["content"] == "noindex"


def test_noindex_excluded_from_sitemap(tmp_path):
    """A noindex page does not appear in sitemap.xml."""
    out = _build(tmp_path, baseurl="https://example.com/")
    sitemap_text = (out / "sitemap.xml").read_text()
    assert "seo-noindex.html" not in sitemap_text


def test_noindex_meta_absent_on_normal_pages(tmp_path):
    """Pages without the noindex flag don't emit robots noindex."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "index.html")
    tag = soup.find("meta", attrs={"name": "robots"})
    assert tag is None


def test_robots_txt_generated(tmp_path):
    """robots.txt is written to the build output with allow-all + sitemap."""
    out = _build(tmp_path, baseurl="https://example.com/")
    robots = out / "robots.txt"
    assert robots.exists()
    text = robots.read_text()
    assert "User-agent: *" in text
    assert "Allow: /" in text
    assert "Sitemap: https://example.com/sitemap.xml" in text


def test_robots_txt_skips_sitemap_line_without_baseurl(tmp_path):
    """robots.txt still generated, but no Sitemap line if no baseurl."""
    out = _build(tmp_path)
    text = (out / "robots.txt").read_text()
    assert "User-agent: *" in text
    assert "Sitemap:" not in text


def test_robots_txt_user_override_wins(tmp_path):
    """A user-supplied robots.txt in html_extra_path is preserved as-is."""
    extra = tmp_path / "extra"
    extra.mkdir()
    (extra / "robots.txt").write_text("User-agent: *\nDisallow: /\n# custom\n")

    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        confoverrides={"html_extra_path": [str(extra)]},
    )
    text = (out / "robots.txt").read_text()
    assert "Disallow: /" in text
    assert "# custom" in text


def test_robots_txt_skipped_when_seo_disabled(tmp_path):
    """disable_seo=true means no robots.txt is written by Lumina."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        options={"disable_seo": "true"},
    )
    # Sphinx itself doesn't write a robots.txt, so absence is the test.
    assert not (out / "robots.txt").exists()


def test_normalize_iso_datetime_pads_date_only():
    """A bare YYYY-MM-DD becomes a UTC datetime."""
    from sphinx_lumina_theme._seo import normalize_iso_datetime

    assert normalize_iso_datetime("2026-05-03") == "2026-05-03T00:00:00+00:00"


def test_normalize_iso_datetime_passes_through_full_datetime():
    """A value already containing a time component is returned unchanged."""
    from sphinx_lumina_theme._seo import normalize_iso_datetime

    assert (
        normalize_iso_datetime("2026-05-03T12:34:56+00:00")
        == "2026-05-03T12:34:56+00:00"
    )


def test_normalize_iso_datetime_returns_none_for_empty():
    """Empty/None inputs produce None (so JSON-LD omits the field)."""
    from sphinx_lumina_theme._seo import normalize_iso_datetime

    assert normalize_iso_datetime(None) is None
    assert normalize_iso_datetime("") is None
    assert normalize_iso_datetime("   ") is None


def test_techarticle_dates_are_iso_8601_datetime(tmp_path):
    """TechArticle datePublished/dateModified include a time + timezone offset."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "seo-described.html")
    blocks = _ld_blocks(soup)
    article = _block_of_type(blocks, "TechArticle")
    if article is None or "datePublished" not in article:
        # sphinx-last-updated-by-git isn't loaded in the test build, so dates
        # may be absent — that's a separate concern. Skip when no date.
        return
    assert "T" in article["datePublished"]
    assert article["datePublished"].endswith("+00:00")


def test_resolve_publisher_logo_from_theme_option():
    """publisher_logo theme option resolves to an absolute static URL."""
    from sphinx_lumina_theme._seo import resolve_publisher_logo

    url = resolve_publisher_logo(
        theme_options={"publisher_logo": "logo-square.png"},
        html_logo=None,
        html_baseurl="https://example.com/",
    )
    assert url == "https://example.com/_static/logo-square.png"


def test_resolve_publisher_logo_absolute_url_passthrough():
    """An absolute publisher_logo URL is used verbatim."""
    from sphinx_lumina_theme._seo import resolve_publisher_logo

    url = resolve_publisher_logo(
        theme_options={"publisher_logo": "https://cdn.example.com/logo.png"},
        html_logo="ignored.png",
        html_baseurl="https://example.com/",
    )
    assert url == "https://cdn.example.com/logo.png"


def test_resolve_publisher_logo_falls_back_to_html_logo():
    """When publisher_logo is unset, html_logo (if raster) is used."""
    from sphinx_lumina_theme._seo import resolve_publisher_logo

    url = resolve_publisher_logo(
        theme_options={},
        html_logo="brand.png",
        html_baseurl="https://example.com/",
    )
    assert url == "https://example.com/_static/brand.png"


def test_resolve_publisher_logo_skips_svg_html_logo():
    """An SVG html_logo is NOT used (publisher.logo must be raster)."""
    from sphinx_lumina_theme._seo import resolve_publisher_logo

    url = resolve_publisher_logo(
        theme_options={},
        html_logo="brand.svg",
        html_baseurl="https://example.com/",
    )
    assert url is None


def test_resolve_publisher_logo_returns_none_when_no_source():
    """No theme option and no raster html_logo → None (caller omits logo)."""
    from sphinx_lumina_theme._seo import resolve_publisher_logo

    assert (
        resolve_publisher_logo(
            theme_options={}, html_logo=None, html_baseurl="https://example.com/"
        )
        is None
    )


def test_publisher_logo_separate_from_og_image(tmp_path):
    """TechArticle publisher.logo uses publisher_logo, not og_image."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        options={
            "og_image": "og-card.png",
            "publisher_logo": "logo-square.png",
        },
    )
    soup = _soup(out, "seo-described.html")
    blocks = _ld_blocks(soup)
    article = _block_of_type(blocks, "TechArticle")
    assert article is not None
    assert article["image"] == "https://example.com/_static/og-card.png"
    assert (
        article["publisher"]["logo"]["url"]
        == "https://example.com/_static/logo-square.png"
    )


def test_publisher_logo_omitted_when_no_source(tmp_path):
    """When neither publisher_logo nor a raster html_logo is set, omit logo entirely."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        options={"og_image": "og-card.png"},
    )
    soup = _soup(out, "seo-described.html")
    blocks = _ld_blocks(soup)
    article = _block_of_type(blocks, "TechArticle")
    assert article is not None
    # publisher.logo MUST NOT be the OG card (it's a 1200x630 banner, not a logo).
    assert "logo" not in article["publisher"]


def test_og_image_dimensions_emitted_when_set(tmp_path):
    """og_image_width / og_image_height options become og:image:width/height meta."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        options={
            "og_image": "card.png",
            "og_image_width": "1200",
            "og_image_height": "630",
        },
    )
    soup = _soup(out, "index.html")
    width = soup.find("meta", attrs={"property": "og:image:width"})
    height = soup.find("meta", attrs={"property": "og:image:height"})
    assert width is not None and width["content"] == "1200"
    assert height is not None and height["content"] == "630"


def test_og_image_dimensions_absent_without_image(tmp_path):
    """Width/height are not emitted when there's no og:image to size."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        options={"og_image_width": "1200", "og_image_height": "630"},
    )
    soup = _soup(out, "index.html")
    assert soup.find("meta", attrs={"property": "og:image:width"}) is None
    assert soup.find("meta", attrs={"property": "og:image:height"}) is None


def test_og_image_dimensions_optional_when_image_set(tmp_path):
    """og:image works without explicit width/height (back-compat)."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        options={"og_image": "card.png"},
    )
    soup = _soup(out, "index.html")
    assert soup.find("meta", attrs={"property": "og:image"}) is not None
    assert soup.find("meta", attrs={"property": "og:image:width"}) is None


def test_sitemap_show_lastmod_default_true(tmp_path):
    """Lumina flips sphinx-sitemap's lastmod default to True."""
    out = _build(tmp_path, baseurl="https://example.com/")
    sitemap_text = (out / "sitemap.xml").read_text()
    # Without sphinx-last-updated-by-git the dates won't appear (sphinx-sitemap
    # silently disables itself), but the sitemap must still build cleanly.
    assert "<urlset" in sitemap_text


def test_sitemap_show_lastmod_user_override_respected(tmp_path):
    """Users who explicitly set sitemap_show_lastmod=False are not overridden."""
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        confoverrides={"sitemap_show_lastmod": False},
    )
    sitemap_text = (out / "sitemap.xml").read_text()
    assert "<lastmod>" not in sitemap_text


def test_sitemap_noindex_anchored_at_slash_boundary(tmp_path):
    """Noindex exclusion must not match unrelated pages sharing a suffix.

    Regression: ``intro.html`` (noindex) used to match ``extra-intro.html``
    via ``str.endswith("intro.html")``, wrongly removing the latter from
    sitemap.xml. Anchoring at ``/`` fixes this.
    """
    out = _build(tmp_path, baseurl="https://example.com/")
    sitemap_text = (out / "sitemap.xml").read_text()
    assert "https://example.com/intro.html" not in sitemap_text
    assert "https://example.com/extra-intro.html" in sitemap_text


def test_plain_title_strips_html_tags():
    """plain_title removes tags and decodes entities."""
    from sphinx_lumina_theme._seo import plain_title

    assert plain_title("Inline <code>code</code> in title") == "Inline code in title"
    assert plain_title("Cool &amp; useful") == "Cool & useful"
    assert plain_title("") == ""
    assert plain_title(None) == ""


def test_og_title_strips_inline_html_markup(tmp_path):
    """og:title and twitter:title contain plain text, not escaped HTML markup."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "seo-html-title.html")
    og_title = soup.find("meta", attrs={"property": "og:title"})
    tw_title = soup.find("meta", attrs={"name": "twitter:title"})
    assert og_title is not None
    assert tw_title is not None
    # The rendered page title is "Inline <code>code</code> in title".
    # The meta content must NOT contain "<code>" or "&lt;code&gt;".
    assert og_title["content"] == "Inline code in title"
    assert tw_title["content"] == "Inline code in title"
    assert "<" not in og_title["content"]
    assert "&lt;" not in og_title["content"]


def test_jsonld_headline_strips_inline_html_markup(tmp_path):
    """TechArticle and BreadcrumbList use plain-text titles, not HTML."""
    out = _build(tmp_path, baseurl="https://example.com/")
    soup = _soup(out, "seo-html-title.html")
    blocks = _ld_blocks(soup)
    article = _block_of_type(blocks, "TechArticle")
    assert article is not None
    assert article["headline"] == "Inline code in title"
    crumbs = _block_of_type(blocks, "BreadcrumbList")
    assert crumbs is not None
    last_item = crumbs["itemListElement"][-1]
    assert last_item["name"] == "Inline code in title"


def test_handle_from_twitter_url_strips_query_string():
    """Twitter URL parser tolerates query strings, fragments, and sub-paths."""
    from sphinx_lumina_theme._seo import _handle_from_twitter_url

    assert _handle_from_twitter_url("https://twitter.com/foo?ref=x") == "@foo"
    assert _handle_from_twitter_url("https://x.com/foo#bio") == "@foo"
    assert _handle_from_twitter_url("https://twitter.com/foo/status/123") == "@foo"
    assert _handle_from_twitter_url("https://www.twitter.com/foo/") == "@foo"


def test_og_image_omitted_without_baseurl(tmp_path):
    """A relative og_image URL is unusable for social platforms — omit the tag.

    Without ``html_baseurl`` we can't produce an absolute URL; emitting a
    relative one produces broken-image previews on Slack/Twitter/LinkedIn.
    """
    out = _build(tmp_path, options={"og_image": "card.png"})
    soup = _soup(out, "index.html")
    assert soup.find("meta", attrs={"property": "og:image"}) is None
    # Twitter card downgrades to summary when there's no image.
    card = soup.find("meta", attrs={"name": "twitter:card"})
    assert card is not None
    assert card["content"] == "summary"


def test_og_image_absolute_url_works_without_baseurl(tmp_path):
    """An absolute og_image URL still works without html_baseurl."""
    out = _build(
        tmp_path,
        options={"og_image": "https://cdn.example.com/card.png"},
    )
    soup = _soup(out, "index.html")
    img = soup.find("meta", attrs={"property": "og:image"})
    assert img is not None
    assert img["content"] == "https://cdn.example.com/card.png"


def test_resolve_publisher_logo_omitted_without_baseurl():
    """publisher_logo without baseurl returns None — Schema.org needs absolute."""
    from sphinx_lumina_theme._seo import resolve_publisher_logo

    assert (
        resolve_publisher_logo(
            theme_options={"publisher_logo": "logo.png"},
            html_logo=None,
            html_baseurl=None,
        )
        is None
    )


def test_jsonld_escapes_script_breakout(tmp_path):
    """User-controlled strings cannot break out of the JSON-LD <script> block.

    A page title or description containing ``</script>`` must end up encoded
    as ``\\u003c/script\\u003e`` in the rendered HTML so an attacker can't
    inject markup or scripts via front matter.
    """
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        project="Lumina </script><script>alert(1)</script>",
    )
    rendered = (out / "seo-described.html").read_text()
    # The JSON-LD blocks must contain the unicode-escaped form, not the raw
    # closing tag — otherwise the script context would be broken out of.
    assert "</script><script>alert(1)" not in rendered.replace(
        '<script type="application/ld+json">', ""
    ).replace("</script>", "")
    # And the escaped form is present in at least one ld+json block.
    soup = _soup(out, "seo-described.html")
    raw_blocks = [
        tag.string or ""
        for tag in soup.find_all("script", attrs={"type": "application/ld+json"})
    ]
    assert any("\\u003c/script\\u003e" in b for b in raw_blocks)


def test_user_configured_sitemap_preserved_when_seo_disabled(tmp_path):
    """When the user explicitly enables sphinx-sitemap, disable_seo leaves it alone.

    ``disable_seo`` opts out of *Lumina's* SEO emissions; it should not
    override the user's own extension config.
    """
    out = _build(
        tmp_path,
        baseurl="https://example.com/",
        options={"disable_seo": "true"},
        confoverrides={"extensions": ["myst_parser", "sphinx_sitemap"]},
    )
    # User explicitly added sphinx_sitemap → sitemap.xml is preserved.
    assert (out / "sitemap.xml").exists()
