"""Test search modal markup."""


def test_search_modal_exists(index_html):
    """Page should have a search modal element."""
    modal = index_html.find(id="lumina-search-modal")
    assert modal is not None


def test_search_modal_has_input(index_html):
    """Search modal should have an input field."""
    modal = index_html.find(id="lumina-search-modal")
    search_input = modal.find("input", attrs={"type": "search"})
    assert search_input is not None, "Missing search input in modal"


def test_search_base_url_meta_tag(index_html):
    """Page should have a lumina-base-url meta tag for search path resolution."""
    meta = index_html.find("meta", attrs={"name": "lumina-base-url"})
    assert meta is not None, "Missing lumina-base-url meta tag"
    assert meta.get("content"), "lumina-base-url meta tag should have content"
