"""Test dark mode functionality."""


def test_dark_mode_preload_script(index_html):
    """Head should contain inline script that sets data-theme from localStorage."""
    head = index_html.find("head")
    scripts = head.find_all("script")
    has_preload = any(
        s.string and "lumina-theme" in s.string and "localStorage" in s.string
        for s in scripts
    )
    assert has_preload, "Missing dark mode preload script"


def test_theme_toggle_button_exists(index_html):
    """Page should have a theme toggle button."""
    btn = index_html.find(attrs={"data-theme-toggle": True})
    assert btn is not None
