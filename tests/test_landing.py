"""Test the landing page template."""

import pytest
from bs4 import BeautifulSoup
from conftest import copy_sample_docs, sphinx_app


def build_landing(tmp_path):
    """Build sample docs with a landing page and return parsed HTML."""
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    out_dir = tmp_path / "build"

    conf_py = conf_dir / "conf.py"
    conf_py.write_text(
        'project = "Test"\n'
        'extensions = ["myst_parser"]\n'
        'html_theme = "lumina"\n'
        'exclude_patterns = ["_build"]\n'
    )

    copy_sample_docs(conf_dir)

    app = sphinx_app(conf_dir, out_dir)
    app.build()
    return BeautifulSoup((out_dir / "landing-test.html").read_text(), "html.parser")


@pytest.fixture(scope="module")
def landing_html(tmp_path_factory):
    """Build the landing page once for the module and return parsed BeautifulSoup."""
    tmp_path = tmp_path_factory.mktemp("landing")
    return build_landing(tmp_path)


def test_landing_hero_renders_title(landing_html):
    """Landing page should render hero title from metadata."""
    hero = landing_html.find(class_="lumina-hero")
    assert hero is not None, "Hero section not found"
    assert "Test Landing" in hero.get_text()


def test_landing_hero_renders_subtitle(landing_html):
    """Landing page should render hero subtitle from metadata."""
    hero = landing_html.find(class_="lumina-hero")
    assert "A subtitle for testing" in hero.get_text()


def test_landing_hero_renders_primary_cta(landing_html):
    """Landing page should render primary CTA button."""
    primary_btn = landing_html.find(class_="lumina-hero-btn-primary")
    assert primary_btn is not None, "Primary CTA button not found"
    assert "Get Started" in primary_btn.get_text()


def test_landing_hero_renders_tags(landing_html):
    """Landing page should render feature tags from metadata."""
    tags = landing_html.find(class_="lumina-hero-tags")
    assert tags is not None, "Tags section not found"
    assert "Fast" in tags.get_text()
    assert "Modern" in tags.get_text()


def test_landing_no_sidebar(landing_html):
    """Landing page should not have a sidebar."""
    sidebar = landing_html.find(id="lumina-sidebar")
    assert sidebar is None, "Landing page should not have a sidebar"


def test_landing_no_hero_without_metadata(tmp_path):
    """Landing page without hero metadata should not render hero section."""
    conf_dir = tmp_path / "conf2"
    conf_dir.mkdir()
    out_dir = tmp_path / "build2"

    conf_py = conf_dir / "conf.py"
    conf_py.write_text(
        'project = "Test"\n'
        'extensions = ["myst_parser"]\n'
        'html_theme = "lumina"\n'
        'exclude_patterns = ["_build"]\n'
    )

    landing_md = conf_dir / "bare-landing.md"
    landing_md.write_text(
        "---\ntemplate: landing.html\n---\n\n# Bare Landing\n\nJust content.\n"
    )
    index_md = conf_dir / "index.md"
    index_md.write_text("# Home\n\n```{toctree}\n:hidden:\nbare-landing\n```\n")

    app = sphinx_app(conf_dir, out_dir)
    app.build()
    html = BeautifulSoup((out_dir / "bare-landing.html").read_text(), "html.parser")
    hero = html.find(class_="lumina-hero")
    assert hero is None, "Hero should not render without hero_title metadata"
