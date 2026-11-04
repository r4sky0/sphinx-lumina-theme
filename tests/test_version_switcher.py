"""Test the version switcher dropdown."""

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
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    out_dir = tmp_path / "build"

    (conf_dir / "conf.py").write_text(
        'project = "Test"\n'
        'extensions = ["myst_parser"]\n'
        'html_theme = "lumina"\n'
        'html_theme_options = {"version_switcher_json": "https://example.com/versions.json"}\n'
        'exclude_patterns = ["_build"]\n'
    )

    copy_sample_docs(conf_dir)

    app = sphinx_app(conf_dir, out_dir)
    # Build should succeed (warning, not error)
    app.build()

    html = BeautifulSoup((out_dir / "index.html").read_text(), "html.parser")
    switcher = html.find(id="lumina-version-switcher")
    assert switcher is not None, "Switcher should still render even without match"


def test_switcher_uses_readthedocs_versions(tmp_path, monkeypatch):
    """On Read the Docs the switcher renders without JSON and reads addons data."""
    monkeypatch.setenv("READTHEDOCS", "True")
    monkeypatch.setenv("READTHEDOCS_VERSION", "latest")
    html = _build_with_options(tmp_path)
    switcher = html.find(id="lumina-version-switcher")
    assert switcher.get("data-source") == "readthedocs"
    assert switcher.get("data-version-match") == "latest"
    assert not switcher.has_attr("data-json-url")
    assert html.find("meta", attrs={"name": "readthedocs-addons-api-version"})


def test_switcher_json_wins_on_readthedocs(tmp_path, monkeypatch):
    """An explicit version_switcher_json keeps priority over the addons data."""
    monkeypatch.setenv("READTHEDOCS", "True")
    html = _build_with_options(
        tmp_path,
        {
            "version_switcher_json": "https://example.com/versions.json",
            "version_switcher_match": "1.17",
        },
    )
    switcher = html.find(id="lumina-version-switcher")
    assert switcher.get("data-json-url") == "https://example.com/versions.json"
    assert not switcher.has_attr("data-source")


def test_no_addons_meta_off_readthedocs(index_html):
    """The addons API meta tag is only emitted for Read the Docs builds."""
    assert not index_html.find("meta", attrs={"name": "readthedocs-addons-api-version"})


def test_readthedocs_canonical_url_default(tmp_path, monkeypatch):
    """READTHEDOCS_CANONICAL_URL fills in html_baseurl when it is unset."""
    monkeypatch.setenv("READTHEDOCS_CANONICAL_URL", "https://example.org/en/latest/")
    html = _build_with_options(tmp_path)
    canonical = html.find("link", rel="canonical")
    assert canonical["href"] == "https://example.org/en/latest/index.html"
