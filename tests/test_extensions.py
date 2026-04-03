"""Test extension-rendered content in the theme."""

from bs4 import BeautifulSoup
from sphinx.application import Sphinx


def test_sphinx_design_tabs(index_html):
    """Tab set should render with sphinx-design structure."""
    tab_labels = index_html.find_all(class_="sd-tab-label")
    assert len(tab_labels) >= 2, (
        f"Expected at least 2 tab labels, got {len(tab_labels)}"
    )


def test_sphinx_design_cards(index_html):
    """Card grid should render with sphinx-design structure."""
    cards = index_html.find_all(class_="sd-card")
    assert len(cards) >= 2, f"Expected at least 2 cards, got {len(cards)}"


def test_mermaid_diagram(tmp_path):
    """Mermaid diagram container should be present when extension is loaded."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "conf.py").write_text(
        'project = "Mermaid Test"\n'
        'extensions = ["myst_parser", "sphinxcontrib.mermaid"]\n'
        'html_theme = "lumina"\n'
    )
    (src / "index.md").write_text(
        "# Test\n\n```{mermaid}\ngraph LR\n    A --> B\n```\n"
    )
    out = tmp_path / "build"
    app = Sphinx(str(src), str(src), str(out), str(out / ".dt"), "html", freshenv=True)
    app.build()
    html = BeautifulSoup((out / "index.html").read_text(), "html.parser")
    mermaid = html.find(class_="mermaid")
    assert mermaid is not None, "Missing mermaid diagram element"


def test_copybutton_script_loaded(index_html):
    """sphinx-copybutton should include its JS script."""
    scripts = index_html.find_all("script")
    copybutton_loaded = any("copybutton" in (s.get("src") or "") for s in scripts)
    assert copybutton_loaded, "copybutton.js script not loaded"
