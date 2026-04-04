"""Test HTTP domain styling and api_base_url theme option."""

from bs4 import BeautifulSoup
from sphinx.application import Sphinx

_BASE_RST = (
    "HTTP Test\n"
    "=========\n\n"
    ".. http:get:: /tasks\n\n"
    "   Returns all tasks.\n\n"
    "   :query status: Filter by status.\n"
    "   :status 200: An array of tasks.\n\n"
    ".. http:post:: /tasks\n\n"
    "   Creates a new task.\n\n"
    "   :<json string title: Task title.\n"
    "   :reqheader Authorization: Bearer token.\n"
    "   :reqheader Content-Type: ``application/json``\n"
    "   :status 201: Created.\n\n"
    ".. http:delete:: /tasks/(int:task_id)\n\n"
    "   Deletes a task.\n\n"
    "   :param task_id: The task ID.\n"
    "   :status 204: Deleted.\n"
)


def _build_http_site(tmp_path, theme_options=None, rst_content=None):
    """Build a minimal site with HTTP domain endpoints."""
    src = tmp_path / "src"
    src.mkdir()

    opts_str = repr(theme_options or {})

    (src / "conf.py").write_text(
        'project = "HTTP Test"\n'
        'extensions = ["sphinxcontrib.httpdomain"]\n'
        'html_theme = "lumina"\n'
        f"html_theme_options = {opts_str}\n"
    )
    (src / "index.rst").write_text(rst_content or _BASE_RST)

    out = tmp_path / "build"
    app = Sphinx(str(src), str(src), str(out), str(out / ".dt"), "html", freshenv=True)
    app.build()
    return BeautifulSoup((out / "index.html").read_text(), "html.parser")


def test_http_endpoints_render(tmp_path):
    """HTTP domain directives should produce dl.http elements with method classes."""
    html = _build_http_site(tmp_path)
    get_dl = html.find("dl", class_=["http", "get"])
    post_dl = html.find("dl", class_=["http", "post"])
    delete_dl = html.find("dl", class_=["http", "delete"])
    assert get_dl is not None, "Missing dl.http.get element"
    assert post_dl is not None, "Missing dl.http.post element"
    assert delete_dl is not None, "Missing dl.http.delete element"


def test_http_signature_cards(tmp_path):
    """Each HTTP endpoint should have a dt.sig signature card."""
    html = _build_http_site(tmp_path)
    endpoints = html.find_all("dl", class_="http")
    for dl in endpoints:
        sig = dl.find("dt", class_="sig")
        assert sig is not None, f"Missing dt.sig in {dl.get('class')}"


def test_api_base_url_data_attribute(tmp_path):
    """api_base_url theme option should output a data attribute on <html>."""
    html = _build_http_site(tmp_path, {"api_base_url": "https://api.example.com/v1"})
    # The data attribute is set via an inline script, so check for the script content
    scripts = html.find_all("script")
    found = any("apiBaseUrl" in (s.string or "") for s in scripts)
    assert found, "Missing apiBaseUrl data attribute script"


def test_no_api_base_url_by_default(tmp_path):
    """Without api_base_url, no apiBaseUrl script should appear."""
    html = _build_http_site(tmp_path)
    scripts = html.find_all("script")
    found = any("apiBaseUrl" in (s.string or "") for s in scripts)
    assert not found, "apiBaseUrl script should not appear without theme option"


def test_lumina_js_loaded(tmp_path):
    """lumina.js should be loaded (carries the curl-copy module)."""
    html = _build_http_site(tmp_path)
    scripts = html.find_all("script")
    lumina_loaded = any("lumina.js" in (s.get("src") or "") for s in scripts)
    assert lumina_loaded, "lumina.js script not loaded"


# ── try_it_out theme option ────────────────────────────────────────────────


def test_try_it_out_disabled(tmp_path):
    """try_it_out='false' should inject the tryItOut='false' data attribute script."""
    html = _build_http_site(
        tmp_path,
        {"api_base_url": "https://api.example.com/v1", "try_it_out": "false"},
    )
    scripts = html.find_all("script")
    found = any("tryItOut" in (s.string or "") for s in scripts)
    assert found, "Missing tryItOut disable script when try_it_out='false'"


def test_try_it_out_enabled_by_default(tmp_path):
    """Without try_it_out option, no tryItOut disable script should appear."""
    html = _build_http_site(tmp_path, {"api_base_url": "https://api.example.com/v1"})
    scripts = html.find_all("script")
    found = any("tryItOut" in (s.string or "") for s in scripts)
    assert not found, (
        "tryItOut disable script must not appear when try_it_out is not set"
    )


def test_try_it_out_explicit_true(tmp_path):
    """try_it_out='true' should not inject any disable script."""
    html = _build_http_site(
        tmp_path,
        {"api_base_url": "https://api.example.com/v1", "try_it_out": "true"},
    )
    scripts = html.find_all("script")
    found = any("tryItOut" in (s.string or "") for s in scripts)
    assert not found, "tryItOut disable script must not appear when try_it_out='true'"


# ── Per-block base URL override ────────────────────────────────────────────

_ANCESTOR_OVERRIDE_RST = (
    "HTTP Test\n"
    "=========\n\n"
    "Global endpoint:\n\n"
    ".. http:get:: /global\n\n"
    "   Uses the global API base URL.\n\n"
    "   :status 200: OK.\n\n"
    "Override block:\n\n"
    ".. raw:: html\n\n"
    '   <div data-api-base-url="https://other.api.com/v2">\n\n'
    ".. http:get:: /override\n\n"
    "   Uses a different API base URL.\n\n"
    "   :status 200: OK.\n\n"
    ".. raw:: html\n\n"
    "   </div>\n"
)


def test_ancestor_override_attribute_present(tmp_path):
    """A raw div with data-api-base-url should appear in the built HTML."""
    html = _build_http_site(
        tmp_path,
        {"api_base_url": "https://global.api.com"},
        rst_content=_ANCESTOR_OVERRIDE_RST,
    )
    override_div = html.find(attrs={"data-api-base-url": "https://other.api.com/v2"})
    assert override_div is not None, (
        "Per-block data-api-base-url wrapper not found in built HTML"
    )


def test_ancestor_override_wraps_endpoint(tmp_path):
    """The endpoint inside the override wrapper should be a descendant of the div."""
    html = _build_http_site(
        tmp_path,
        {"api_base_url": "https://global.api.com"},
        rst_content=_ANCESTOR_OVERRIDE_RST,
    )
    override_div = html.find(attrs={"data-api-base-url": "https://other.api.com/v2"})
    assert override_div is not None
    dl = override_div.find("dl", class_="http")
    assert dl is not None, (
        "dl.http endpoint should be a descendant of the data-api-base-url wrapper"
    )


def test_global_endpoint_not_in_override_wrapper(tmp_path):
    """The global endpoint should NOT be inside the per-block override div."""
    html = _build_http_site(
        tmp_path,
        {"api_base_url": "https://global.api.com"},
        rst_content=_ANCESTOR_OVERRIDE_RST,
    )
    override_div = html.find(attrs={"data-api-base-url": "https://other.api.com/v2"})
    assert override_div is not None
    # The dl.http elements outside the wrapper use the global URL
    all_dls = html.find_all("dl", class_="http")
    wrapped_dls = override_div.find_all("dl", class_="http")
    assert len(all_dls) > len(wrapped_dls), (
        "Some dl.http endpoints should be outside the per-block override div"
    )
