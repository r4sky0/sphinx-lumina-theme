"""Test llms.txt integration."""

from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from sphinx.application import Sphinx


def test_no_llms_txt_link_by_default(build_output):
    """When sphinx-llm is not installed, no llms.txt link tag should appear."""
    html_path = build_output / "index.html"
    soup = BeautifulSoup(html_path.read_text(), "html.parser")
    link = soup.find("link", attrs={"href": lambda v: v and "llms.txt" in v})
    assert link is None, "llms.txt link should not appear without sphinx-llm extension"


@pytest.fixture(scope="module")
def build_with_llms_txt(tmp_path_factory):
    """Build sample docs with sphinx_llm.txt faked in extensions."""
    src_dir = Path(__file__).parent / "sample_docs"
    out_dir = tmp_path_factory.mktemp("build_llms")
    doctree_dir = out_dir / ".doctrees"

    confoverrides = {
        "extensions": [
            "myst_parser",
            "sphinx_design",
            "sphinx_copybutton",
        ],
    }

    app = Sphinx(
        srcdir=str(src_dir),
        confdir=str(src_dir),
        outdir=str(out_dir),
        doctreedir=str(doctree_dir),
        buildername="html",
        freshenv=True,
        confoverrides=confoverrides,
    )
    # Inject a fake extension entry before build(). This works because
    # _add_context is a write-phase hook that reads app.extensions at
    # render time, not at Sphinx init time.
    from sphinx.extension import Extension

    app.extensions["sphinx_llm.txt"] = Extension(
        "sphinx_llm.txt", module=None, version="fake"
    )
    app.build()
    return out_dir


def test_llms_txt_link_present_when_extension_loaded(build_with_llms_txt):
    """When sphinx-llm is loaded, a <link> tag pointing to llms.txt should appear."""
    html_path = build_with_llms_txt / "index.html"
    soup = BeautifulSoup(html_path.read_text(), "html.parser")
    link = soup.find("link", attrs={"href": lambda v: v and "llms.txt" in v})
    assert link is not None, (
        "llms.txt <link> tag should appear when extension is loaded"
    )
    assert link.get("rel") == ["alternate"]
    assert link.get("type") == "text/markdown"
