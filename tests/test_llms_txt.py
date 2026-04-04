"""Test llms.txt integration."""

from bs4 import BeautifulSoup


def test_no_llms_txt_link_by_default(build_output):
    """When sphinx-llm is not installed, no llms.txt link tag should appear."""
    html_path = build_output / "index.html"
    soup = BeautifulSoup(html_path.read_text(), "html.parser")
    link = soup.find("link", attrs={"href": lambda v: v and "llms.txt" in v})
    assert link is None, "llms.txt link should not appear without sphinx-llm extension"
