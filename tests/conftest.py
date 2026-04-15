"""Shared test fixtures for sphinx-lumina-theme tests."""

import shutil
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest
from sphinx.application import Sphinx

SAMPLE_DOCS = Path(__file__).parent / "sample_docs"


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
    src_dir = Path(__file__).parent / "sample_docs"
    out_dir = tmp_path_factory.mktemp("build")
    doctree_dir = out_dir / ".doctrees"

    app = Sphinx(
        srcdir=str(src_dir),
        confdir=str(src_dir),
        outdir=str(out_dir),
        doctreedir=str(doctree_dir),
        buildername="html",
        freshenv=True,
    )
    app.build()
    return out_dir


@pytest.fixture(scope="session")
def wide_build_output(tmp_path_factory):
    """Build sample docs with wide_layout enabled."""
    src_dir = Path(__file__).parent / "sample_docs"
    out_dir = tmp_path_factory.mktemp("wide_build")
    doctree_dir = out_dir / ".doctrees"

    app = Sphinx(
        srcdir=str(src_dir),
        confdir=str(src_dir),
        outdir=str(out_dir),
        doctreedir=str(doctree_dir),
        buildername="html",
        freshenv=True,
        confoverrides={"html_theme_options.wide_layout": "toggle"},
    )
    app.build()
    return out_dir


@pytest.fixture(scope="session")
def always_wide_build_output(tmp_path_factory):
    """Build sample docs with wide_layout set to always."""
    src_dir = Path(__file__).parent / "sample_docs"
    out_dir = tmp_path_factory.mktemp("always_wide_build")
    doctree_dir = out_dir / ".doctrees"

    app = Sphinx(
        srcdir=str(src_dir),
        confdir=str(src_dir),
        outdir=str(out_dir),
        doctreedir=str(doctree_dir),
        buildername="html",
        freshenv=True,
        confoverrides={"html_theme_options.wide_layout": "always"},
    )
    app.build()
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

    subprocess.run(
        ["uv", "run", "sphinx-build", str(project_root / "docs"), str(out_dir)],
        cwd=str(project_root),
        check=True,
    )

    port = _find_free_port()

    server = subprocess.Popen(
        ["python", "-m", "http.server", str(port)],
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
