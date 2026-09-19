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


def test_search_input_exposes_combobox_state(index_html):
    """Search input should expose the active result to assistive technology."""
    search_input = index_html.find("input", id="lumina-search-input")
    assert search_input is not None
    assert search_input.get("role") == "combobox"
    assert search_input.get("aria-controls") == "lumina-search-results"
    assert search_input.get(":aria-activedescendant")


def test_search_results_use_listbox_pattern(index_html):
    """Search results should have a labelled listbox container."""
    results = index_html.find(id="lumina-search-results")
    assert results is not None
    assert results.get("role") == "listbox"
    assert results.get("aria-label") == "Search results"


def test_search_messages_are_delivered_with_the_page(index_html):
    """JavaScript search states should be available for Sphinx translation."""
    messages = index_html.find("script", id="lumina-i18n")
    assert messages is not None
    assert "Pagefind is unavailable" in messages.text
