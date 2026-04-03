"""Browser-based tests using Playwright."""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True)
def _goto_index(page: Page, live_server: str):
    """Navigate to the site index before each test."""
    page.goto(live_server)
    page.wait_for_function("() => window.Alpine !== undefined")


def test_search_modal_opens(page: Page):
    """Clicking search trigger should open the search modal."""
    page.click("[data-search-trigger]")
    modal = page.locator("#lumina-search-modal")
    expect(modal).to_be_visible()
    search_input = modal.locator("input[type='search']")
    expect(search_input).to_be_focused()


def test_search_modal_closes_on_escape(page: Page):
    """Pressing Escape should close the search modal."""
    page.click("[data-search-trigger]")
    expect(page.locator("#lumina-search-modal")).to_be_visible()
    page.keyboard.press("Escape")
    expect(page.locator("#lumina-search-modal")).to_be_hidden()


def test_search_returns_results(page: Page, live_server: str):
    """Typing a query should produce search results."""
    page.click("[data-search-trigger]")
    page.locator("#lumina-search-modal input[type='search']").fill("getting started")
    page.wait_for_selector("#lumina-search-modal a[href]", timeout=10000)
    results = page.locator("#lumina-search-modal a[href]")
    assert results.count() >= 1


def test_theme_toggle_cycles(page: Page):
    """Clicking theme toggle should cycle through modes."""
    toggle = page.locator("[data-theme-toggle]")

    # auto -> light
    toggle.click()
    expect(page.locator("html")).to_have_attribute("data-theme", "light")

    # light -> dark
    toggle.click()
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")

    # dark -> auto
    toggle.click()
    data_theme = page.locator("html").get_attribute("data-theme")
    assert data_theme in ("light", "dark")


def test_theme_persists_on_reload(page: Page, live_server: str):
    """Toggling to dark should persist after page reload."""
    toggle = page.locator("[data-theme-toggle]")
    # auto -> light -> dark
    toggle.click()
    toggle.click()
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")

    page.reload()
    page.wait_for_function("() => window.Alpine !== undefined")
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")


def test_mobile_sidebar(page: Page, live_server: str):
    """On mobile viewport, hamburger should open sidebar drawer."""
    # Use a regular page (not landing) where sidebar is rendered
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(f"{live_server}/getting-started.html")
    page.wait_for_function("() => window.Alpine !== undefined")

    hamburger = page.locator("[data-sidebar-toggle]")
    hamburger.click()

    # Drawer is teleported to body via Alpine x-teleport
    drawer = page.locator("#lumina-sidebar-drawer")
    expect(drawer).to_be_visible(timeout=3000)


def test_toc_scrollspy(page: Page, live_server: str):
    """Scrolling should activate a TOC link via scrollspy."""
    # TOC sidebar requires xl breakpoint (1280px+)
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{live_server}/getting-started.html")
    page.wait_for_function("() => window.Alpine !== undefined")

    # Scroll to a heading further down the page
    page.locator("#next-steps").scroll_into_view_if_needed()
    # Wait for IntersectionObserver to fire and verify any link gets active class
    active = page.locator(".lumina-toc-nav a.lumina-toc-active")
    expect(active).to_have_count(1, timeout=3000)


def test_breadcrumbs_link(page: Page, live_server: str):
    """Getting-started page should have breadcrumb with link to index."""
    page.goto(f"{live_server}/getting-started.html")
    page.wait_for_function("() => window.Alpine !== undefined")

    breadcrumb = page.locator("nav[aria-label='Breadcrumb']")
    expect(breadcrumb).to_be_visible()
    home_link = breadcrumb.locator("a").first
    expect(home_link).to_be_visible()


def test_prev_next_navigation(page: Page, live_server: str):
    """Getting-started page should have prev/next navigation cards."""
    page.goto(f"{live_server}/getting-started.html")
    page.wait_for_function("() => window.Alpine !== undefined")

    footer_nav = page.locator("nav[aria-label='Page navigation']")
    expect(footer_nav).to_be_visible()
    nav_links = footer_nav.locator("a")
    assert nav_links.count() >= 1
