"""Test separate light/dark logo rendering."""

import shutil
from pathlib import Path

from bs4 import BeautifulSoup
from sphinx.application import Sphinx


def _build_with_logos(tmp_path, options=None, create_logos=True):
    """Build sample docs with logo options and return parsed index HTML."""
    src_dir = Path(__file__).parent / "sample_docs"
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    out_dir = tmp_path / "build"
    doctree_dir = out_dir / ".doctrees"

    static_dir = conf_dir / "_static"
    static_dir.mkdir()
    if create_logos:
        (static_dir / "logo-light.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><circle cx="16" cy="16" r="10" fill="black"/></svg>'
        )
        (static_dir / "logo-dark.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><circle cx="16" cy="16" r="10" fill="white"/></svg>'
        )

    opts = options or {}
    (conf_dir / "conf.py").write_text(
        'project = "Test"\n'
        'extensions = ["myst_parser"]\n'
        'html_theme = "lumina"\n'
        f"html_theme_options = {opts!r}\n"
        'exclude_patterns = ["_build"]\n'
        'html_static_path = ["_static"]\n'
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


def test_default_logo_is_svg_prism(index_html):
    """Without any logo options, the default SVG prism should render."""
    header = index_html.find(id="lumina-header")
    svg = header.find("svg", class_="lumina-logo")
    assert svg is not None, "Default SVG prism logo not found"


def test_both_logos_render_two_images(tmp_path):
    """When both light and dark logos are set, two img tags should render."""
    html = _build_with_logos(
        tmp_path,
        {"light_logo": "logo-light.svg", "dark_logo": "logo-dark.svg"},
    )
    header = html.find(id="lumina-header")
    light_img = header.find("img", class_="lumina-logo-light")
    dark_img = header.find("img", class_="lumina-logo-dark")
    assert light_img is not None, "Light logo img not found"
    assert dark_img is not None, "Dark logo img not found"
    assert "logo-light.svg" in light_img.get("src", "")
    assert "logo-dark.svg" in dark_img.get("src", "")


def test_only_light_logo_renders_single_image(tmp_path):
    """When only light_logo is set, a single img should render."""
    html = _build_with_logos(
        tmp_path,
        {"light_logo": "logo-light.svg"},
    )
    header = html.find(id="lumina-header")
    img = header.find("img")
    assert img is not None, "Logo img not found"
    assert "logo-light.svg" in img.get("src", "")


def test_only_dark_logo_renders_single_image(tmp_path):
    """When only dark_logo is set, a single img should render."""
    html = _build_with_logos(
        tmp_path,
        {"dark_logo": "logo-dark.svg"},
    )
    header = html.find(id="lumina-header")
    img = header.find("img")
    assert img is not None, "Logo img not found"
    assert "logo-dark.svg" in img.get("src", "")


def test_html_logo_fallback(tmp_path):
    """html_logo should work as a fallback when no theme logo options are set."""
    src_dir = Path(__file__).parent / "sample_docs"
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    out_dir = tmp_path / "build"
    doctree_dir = out_dir / ".doctrees"

    static_dir = conf_dir / "_static"
    static_dir.mkdir()
    (static_dir / "mylogo.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" fill="red"/></svg>'
    )

    (conf_dir / "conf.py").write_text(
        'project = "Test"\n'
        'extensions = ["myst_parser"]\n'
        'html_theme = "lumina"\n'
        'html_logo = "_static/mylogo.svg"\n'
        'html_static_path = ["_static"]\n'
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
    html = BeautifulSoup((out_dir / "index.html").read_text(), "html.parser")

    header = html.find(id="lumina-header")
    img = header.find("img")
    assert img is not None, "html_logo fallback img not found"


def test_logos_have_alt_text(tmp_path):
    """Logo images should have alt text with project name."""
    html = _build_with_logos(
        tmp_path,
        {"light_logo": "logo-light.svg", "dark_logo": "logo-dark.svg"},
    )
    header = html.find(id="lumina-header")
    images = header.find_all("img", class_=lambda c: c and "lumina-logo" in c)
    for img in images:
        assert "logo" in img.get("alt", "").lower(), f"Missing alt text on {img}"


def test_no_svg_prism_when_logos_set(tmp_path):
    """Default SVG prism should not render when logos are provided."""
    html = _build_with_logos(
        tmp_path,
        {"light_logo": "logo-light.svg", "dark_logo": "logo-dark.svg"},
    )
    header = html.find(id="lumina-header")
    svg = header.find("svg", class_="lumina-logo")
    assert svg is None, "SVG prism should not render when logos are set"
