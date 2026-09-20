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
    expect(search_input).to_be_visible()


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


def test_showcase_uses_flat_theme_buttons(page: Page):
    button = page.locator(".lumina-hero-btn-primary")
    expect(button).to_have_css("box-shadow", "none")
    button.hover()
    expect(button).to_have_css("box-shadow", "none")
    expect(button).to_have_css("transform", "none")


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
    page.goto(f"{live_server}/getting-started/installation.html")
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
    page.goto(f"{live_server}/getting-started/installation.html")
    page.wait_for_function("() => window.Alpine !== undefined")

    # Scroll to a heading further down the page
    page.locator("#next-steps").scroll_into_view_if_needed()
    # Wait for IntersectionObserver to fire and verify any link gets active class
    active = page.locator(".lumina-toc-nav a.lumina-toc-active")
    expect(active).to_have_count(1, timeout=3000)


def test_breadcrumbs_link(page: Page, live_server: str):
    """Getting-started page should have breadcrumb with link to index."""
    page.goto(f"{live_server}/getting-started/installation.html")
    page.wait_for_function("() => window.Alpine !== undefined")

    breadcrumb = page.locator("nav[aria-label='Breadcrumb']")
    expect(breadcrumb).to_be_visible()
    home_link = breadcrumb.locator("a").first
    expect(home_link).to_be_visible()


def test_prev_next_navigation(page: Page, live_server: str):
    """Getting-started page should have prev/next navigation cards."""
    page.goto(f"{live_server}/getting-started/installation.html")
    page.wait_for_function("() => window.Alpine !== undefined")

    footer_nav = page.locator("nav[aria-label='Page navigation']")
    expect(footer_nav).to_be_visible()
    nav_links = footer_nav.locator("a")
    assert nav_links.count() >= 1


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_flat_cards_keep_interaction_feedback(page: Page, live_server: str, theme: str):
    """Extension shadow utilities must not override flat cards or hide focus."""
    page.emulate_media(reduced_motion="reduce")
    page.add_init_script(f"localStorage.setItem('lumina-theme', '{theme}')")
    page.goto(f"{live_server}/reference/cards-and-grids.html")

    def appearance(card):
        return card.evaluate(
            """e => {
                const s = getComputedStyle(e);
                return [s.boxShadow, s.transform, s.backgroundColor, s.borderColor];
            }"""
        )

    static_card = page.locator(".sd-card:not(.sd-card-hover)").first
    before = appearance(static_card)
    assert before[:2] == ["none", "none"]
    static_card.hover()
    assert appearance(static_card) == before

    linked_card = page.locator(".sd-card-hover").first
    before = appearance(linked_card)
    linked_card.hover()
    expect(linked_card).to_have_css("box-shadow", "none")
    expect(linked_card).to_have_css("transform", "none")
    assert appearance(linked_card)[2:] != before[2:]

    page.keyboard.press("Tab")
    linked_card.locator("a").first.focus()
    expect(linked_card).to_have_css("outline-style", "solid")
    expect(linked_card).to_have_css("outline-width", "2px")

    navigation_card = page.locator("nav[aria-label='Page navigation'] a").first
    navigation_card.hover()
    expect(navigation_card).to_have_css("box-shadow", "none")
    expect(navigation_card).to_have_css("translate", "none")


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_reading_chrome(page: Page, live_server: str, theme: str):
    """Shared reading layout works beyond the original installation preview."""
    page.emulate_media(reduced_motion="reduce")
    page.add_init_script(f"localStorage.setItem('lumina-theme', '{theme}')")
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.goto(f"{live_server}/guides/search.html")
    expect(page.locator(".lumina-article")).to_have_css("font-size", "16px")
    expect(page.locator(".lumina-article h1")).to_have_css("font-size", "40px")
    expect(page.locator("#lumina-header header")).to_have_css(
        "backdrop-filter", "blur(12px)"
    )

    github = page.locator('.lumina-header-inner a[title="Github"] svg').bounding_box()
    toggle = page.locator("[data-theme-toggle] svg:visible").bounding_box()
    assert (
        abs(github["y"] + github["height"] / 2 - toggle["y"] - toggle["height"] / 2) < 1
    )

    switcher = page.locator("#lumina-section-switcher")
    trigger = switcher.locator("button").first
    expect(trigger).to_have_css("background-color", "rgba(0, 0, 0, 0)")
    trigger.click()
    menu = switcher.locator('[role="menu"]')
    expect(menu).to_be_visible()
    for label in menu.locator(".lumina-section-switcher-desc").all():
        assert label.evaluate("e => e.scrollWidth <= e.clientWidth")
    page.keyboard.press("Tab")
    expect(menu.locator("a").first).to_be_focused()
    page.keyboard.press("Escape")
    expect(menu).to_be_hidden()
    expect(trigger).to_be_focused()
    assert page.locator(".lumina-sidebar-desktop .is-collapsed").count() >= 2

    actions = page.locator(".lumina-page-actions")
    actions.locator("summary").click()
    expect(actions.get_by_role("button", name="Copy page as Markdown")).to_be_visible()
    expect(actions.get_by_role("link", name="Edit this page")).to_be_visible()
    page.keyboard.press("Escape")
    expect(actions).not_to_have_attribute("open", "")
    expect(actions.locator("summary")).to_be_focused()

    for width in (320, 390, 768, 1024, 1440):
        page.set_viewport_size({"width": width, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.set_viewport_size({"width": 390, "height": 844})
    outline = page.locator(".lumina-mobile-outline")
    outline.locator("summary").click()
    expect(outline.locator("a:visible").first).to_be_visible()
    outline.locator("summary").click()
    page.emulate_media(media="print")
    expect(actions).to_be_hidden()
    expect(outline).to_be_hidden()


def test_pagefind_loads_without_errors(page: Page, live_server: str):
    """Pagefind should load from the correct URL without 404 errors.

    Regression test: import() in a classic script resolves relative URLs
    against the script's location (_static/), not the document URL. This
    caused pagefind.js to be fetched from _static/_pagefind/ instead of
    _pagefind/, resulting in a 404.
    """
    failed_requests = []
    page.on("requestfailed", lambda req: failed_requests.append(req.url))

    page.goto(live_server)
    page.wait_for_function("() => window.Alpine !== undefined")

    page.click("[data-search-trigger]")
    modal = page.locator("#lumina-search-modal")
    expect(modal).to_be_visible()

    # Type a query — this triggers Pagefind load + search in one step
    modal.locator("input[type='search']").fill("getting started")

    # Wait for actual result links to appear (Pagefind loaded & returned hits)
    page.wait_for_selector("#lumina-search-modal a[href]", timeout=10000)

    # The "Search requires Pagefind indexing" error must NOT be visible
    error_msg = modal.get_by_text("Search requires Pagefind indexing")
    expect(error_msg).to_have_count(0)

    # No requests to _pagefind/ should have 404'd
    pagefind_failures = [u for u in failed_requests if "_pagefind" in u]
    assert pagefind_failures == [], (
        f"Pagefind resources failed to load: {pagefind_failures}"
    )

    # Pagefind results contain <mark> highlighted excerpts — the Sphinx
    # fallback does not. This confirms the Pagefind backend is active.
    excerpt_html = page.inner_html("#lumina-search-modal a[href] span:last-child")
    assert "<mark>" in excerpt_html, (
        "Expected Pagefind excerpt with <mark> highlights, got Sphinx fallback"
    )
