"""Test HTTP domain styling and api_base_url theme option."""

from bs4 import BeautifulSoup
from sphinx.application import Sphinx


def _build_http_site(tmp_path, theme_options=None):
    """Build a minimal site with an HTTP domain endpoint."""
    src = tmp_path / "src"
    src.mkdir()

    opts = theme_options or {}
    opts_str = repr(opts)

    (src / "conf.py").write_text(
        'project = "HTTP Test"\n'
        'extensions = ["sphinxcontrib.httpdomain"]\n'
        'html_theme = "lumina"\n'
        f"html_theme_options = {opts_str}\n"
    )
    (src / "index.rst").write_text(
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
