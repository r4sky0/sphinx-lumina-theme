"""Shared test fixtures for sphinx-lumina-theme tests."""

import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest
from sphinx.application import Sphinx

SAMPLE_DOCS = Path(__file__).parent / "sample_docs"


def sphinx_app(src_dir, out_dir, **kwargs):
    """Create an HTML Sphinx app for a test site."""
    return Sphinx(
        str(src_dir),
        str(src_dir),
        str(out_dir),
        str(out_dir / ".doctrees"),
        "html",
        freshenv=True,
        **kwargs,
    )


def copy_sample_docs(dest_dir):
    """Copy sample_docs tree into dest_dir, skipping conf.py."""
    for item in SAMPLE_DOCS.iterdir():
        if item.name == "conf.py":
            continue
        if item.is_dir():
            shutil.copytree(item, dest_dir / item.name)
        else:
            shutil.copy2(item, dest_dir / item.name)


@pytest.fixture(scope="session")
def build_output(tmp_path_factory):
    """Build the sample docs with the Lumina theme and return the output path."""
    out_dir = tmp_path_factory.mktemp("build")
    sphinx_app(SAMPLE_DOCS, out_dir).build()
    return out_dir


@pytest.fixture(scope="session")
def wide_build_output(tmp_path_factory):
    """Build sample docs with wide_layout enabled."""
    out_dir = tmp_path_factory.mktemp("wide_build")
    sphinx_app(
        SAMPLE_DOCS, out_dir, confoverrides={"html_theme_options.wide_layout": "toggle"}
    ).build()
    return out_dir


@pytest.fixture(scope="session")
def always_wide_build_output(tmp_path_factory):
    """Build sample docs with wide_layout set to always."""
    out_dir = tmp_path_factory.mktemp("always_wide_build")
    sphinx_app(
        SAMPLE_DOCS, out_dir, confoverrides={"html_theme_options.wide_layout": "always"}
    ).build()
    return out_dir


@pytest.fixture(scope="session")
def index_html(build_output):
    """Return parsed HTML of the index page."""
    from bs4 import BeautifulSoup

    html_path = build_output / "index.html"
    return BeautifulSoup(html_path.read_text(), "html.parser")


@pytest.fixture(scope="session")
def typography_html(build_output):
    """Return parsed HTML of the typography test page."""
    from bs4 import BeautifulSoup

    html_path = build_output / "typography-test.html"
    return BeautifulSoup(html_path.read_text(), "html.parser")


def _find_free_port():
    """Find a free TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def live_server(tmp_path_factory):
    """Build full docs site and serve it on localhost for browser tests."""
    out_dir = tmp_path_factory.mktemp("docs_build")
    project_root = Path(__file__).parent.parent

    sphinx_app(project_root / "docs", out_dir).build()

    port = _find_free_port()

    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd=str(out_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    base_url = f"http://localhost:{port}"
    for _ in range(50):
        try:
            urllib.request.urlopen(base_url)
            break
        except Exception:
            time.sleep(0.1)

    yield base_url

    server.terminate()
    server.wait(timeout=5)
