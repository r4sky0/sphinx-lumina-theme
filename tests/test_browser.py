"""Browser-based tests using Playwright."""

import sys

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
    expect(page.locator("[data-search-trigger]")).to_be_focused()


def test_lightbox_dialog_closes_on_escape(page: Page, live_server: str):
    page.goto(f"{live_server}/reference/images-and-figures.html")
    image = page.locator(".lumina-article img").first
    image.click()
    dialog = page.locator("dialog.lumina-lightbox-overlay")
    expect(dialog).to_be_visible()
    page.keyboard.press("Escape")
    expect(dialog).to_be_hidden()


def test_lightbox_close_button_uses_native_dialog(page: Page, live_server: str):
    page.goto(f"{live_server}/reference/images-and-figures.html")
    page.locator(".lumina-article img").first.click()

    dialog = page.locator("dialog.lumina-lightbox-overlay")
    expect(dialog).to_be_visible()
    close = dialog.get_by_role("button", name="Close preview")
    assert close.evaluate("button => button.form.method") == "dialog"
    close.click()

    expect(dialog).to_be_hidden()
    expect(page.locator("body")).not_to_have_class("lumina-lightbox-open")


def test_fluid_without_offscreen_canvas(page: Page, live_server: str):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.add_init_script(
        "HTMLCanvasElement.prototype.transferControlToOffscreen = undefined;"
        "window.requestIdleCallback = (callback) => { callback(); return 0; };"
    )
    page.goto(live_server)
    expect(page.locator(".lumina-hero-title")).to_be_visible()
    assert not errors


def test_fluid_worker_starts(page: Page, live_server: str):
    page.goto(live_server)
    page.wait_for_function(
        "() => !!window.Alpine.$data(document.querySelector('.lumina-hero'))._worker"
    )


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


@pytest.mark.parametrize(
    "size",
    [
        (1440, 900),
        (1280, 720),
        (768, 1024),
        (390, 844),
        (375, 667),
        (320, 568),
        (844, 390),
    ],
)
def test_showcase_fits_viewport(page: Page, size):
    page.set_viewport_size({"width": size[0], "height": size[1]})
    page.evaluate("document.fonts.ready")
    assert page.evaluate(
        "() => document.documentElement.scrollHeight <= innerHeight"
        " && document.documentElement.scrollWidth <= innerWidth"
    )
    expect(page.locator(".lumina-hero-btn-primary")).to_be_in_viewport()
    expect(page.locator(".lumina-hero-tags")).to_be_in_viewport()


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


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("layout, maximum", [("normal", 800), ("wide", 960)])
def test_article_width_and_navigation_surface(
    page: Page, live_server, theme, layout, maximum
):
    page.goto(f"{live_server}/guides/wide-layout.html")
    page.evaluate(
        "([theme, layout]) => { document.documentElement.dataset.theme = theme;"
        " document.documentElement.dataset.layout = layout; }",
        [theme, layout],
    )
    for width in (390, 1024, 1280, 1920, 2560):
        page.set_viewport_size({"width": width, "height": 900})
        dimensions = page.evaluate("""() => {
            const article = document.querySelector('.lumina-article');
            const sidebar = document.querySelector('#lumina-sidebar');
            const gutter = getComputedStyle(sidebar, '::before');
            return {
                content: document.querySelector('#lumina-content').getBoundingClientRect().width,
                article: article.getBoundingClientRect().width,
                paragraph: article.querySelector('p').getBoundingClientRect().width,
                overflow: document.documentElement.scrollWidth > innerWidth,
                gutterLeft: sidebar.getBoundingClientRect().left - parseFloat(gutter.width),
                gutterColor: gutter.backgroundColor,
                sidebarColor: getComputedStyle(sidebar.querySelector('.lumina-sidebar-desktop')).backgroundColor,
            };
        }""")
        assert dimensions["paragraph"] == pytest.approx(dimensions["article"])
        assert dimensions["content"] <= maximum
        assert not dimensions["overflow"]
        if width >= 1920:
            assert dimensions["content"] == maximum
            assert dimensions["gutterLeft"] <= 0
            assert dimensions["gutterColor"] == dimensions["sidebarColor"]


def test_prose_wrapping_and_optional_hyphenation(page: Page, live_server: str):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{live_server}/guides/wide-layout.html")
    page.locator(".lumina-article p").first.evaluate(
        "p => { const a = document.createElement('a');"
        " a.href = 'https://example.com/' + 'longpath'.repeat(40);"
        " a.textContent = a.href; p.replaceChildren(a); }"
    )
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.add_style_tag(
        content=".lumina-article { -webkit-hyphens: auto; hyphens: auto; }"
    )
    expect(page.locator(".lumina-article p").first).to_have_css("hyphens", "auto")
    expect(page.locator(".lumina-article code").first).to_have_css("hyphens", "none")


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


def test_mobile_tables_stack_rows(page: Page, live_server: str):
    """Wide data tables become labelled rows on narrow screens."""
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(f"{live_server}/reference/lists-and-tables.html")
    page.wait_for_function("() => window.Alpine !== undefined")

    table = page.locator(".lumina-table-stackable").first
    expect(table).to_be_visible()
    expect(table.locator("tbody td").first).to_have_attribute("data-label", "Format")
    assert page.evaluate(
        """(table) => table.scrollWidth <= table.clientWidth""", table.element_handle()
    )


@pytest.mark.parametrize("width", [390, 1440])
def test_interactive_tables(page: Page, live_server: str, width):
    """Opt-in tables filter independently and support keyboard sorting/reset."""
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(f"{live_server}/reference/lists-and-tables.html")
    panel = page.locator(".lumina-table-panel")
    table = panel.locator("table")
    rows = table.locator("tbody tr:visible")
    expect(rows).to_have_count(5)
    expect(
        page.locator("#simple-markdown-tables button.lumina-table-sort")
    ).to_have_count(0)
    search = panel.get_by_role("searchbox", name="Filter rows")
    search.fill(" GUIDE ")
    expect(rows).to_have_count(3)
    expect(panel.get_by_role("status")).to_have_text("3 of 5 rows")
    pages = panel.get_by_role("button", name="Pages")
    pages.focus()
    pages.press("Enter")
    expect(table.locator("th").last).to_have_attribute("aria-sort", "ascending")
    expect(rows.locator("td:last-child")).to_have_text(["4", "8", "12"])
    pages.press("Space")
    expect(rows.locator("td:last-child")).to_have_text(["12", "8", "4"])
    search.fill("no matching entry")
    expect(rows).to_have_count(0)
    expect(panel.locator(".lumina-table-empty")).to_be_visible()
    page.emulate_media(media="print")
    expect(rows).to_have_count(5)
    expect(panel.locator(".lumina-table-toolbar")).to_be_hidden()
    page.emulate_media(media="screen")
    panel.get_by_role("button", name="Reset").click()
    expect(rows.locator("td:last-child")).to_have_text(["4", "24", "12", "8", "36"])
    expect(table.locator("th[aria-sort]")).to_have_count(0)
    expect(panel.get_by_role("button", name="Reset")).to_be_disabled()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    assert not errors


def test_tables_without_javascript(browser, live_server: str):
    context = browser.new_context(java_script_enabled=False)
    page = context.new_page()
    page.goto(f"{live_server}/reference/lists-and-tables.html")
    expect(page.locator("table.lumina-table-interactive tbody tr")).to_have_count(5)
    expect(page.locator(".lumina-table-toolbar")).to_have_count(0)
    context.close()


def test_table_structure_guards_and_independent_state(page: Page, live_server: str):
    simple = """<table class="lumina-table-interactive" id="extra-table">
    <thead><tr><th>Name</th><th>Value</th></tr></thead><tbody>
    <tr><td><a href="#tables">Item 10</a></td><td>-2.5</td></tr>
    <tr><td>Item 2</td><td>10</td></tr>
    <tr><td>Item 1</td><td>0.5</td></tr></tbody></table>"""
    unsupported = [
        simple.replace("<td>10</td>", '<td colspan="2">10</td>'),
        simple.replace("</thead>", "<tr><th>A</th><th>B</th></tr></thead>"),
        simple.replace(
            "</table>", "<tfoot><tr><td>Total</td><td>8</td></tr></tfoot></table>"
        ),
        simple.replace("<th>Name</th>", '<th><a href="#tables">Name</a></th>'),
        simple.replace(
            "</tbody>", "</tbody><tbody><tr><td>A</td><td>1</td></tr></tbody>"
        ),
    ]
    extra = simple + "".join(
        html.replace('id="extra-table"', f'id="unsupported-{index}"')
        for index, html in enumerate(unsupported)
    )

    def inject_tables(route):
        response = route.fetch()
        route.fulfill(
            response=response,
            body=response.text().replace("</article>", extra + "</article>"),
        )

    page.route("**/reference/lists-and-tables.html", inject_tables)
    page.goto(f"{live_server}/reference/lists-and-tables.html")
    expect(page.locator(".lumina-table-panel")).to_have_count(2)
    extra_table = page.locator("#extra-table")
    extra_table.get_by_role("button", name="Value").click()
    expect(extra_table.locator("tbody td:last-child")).to_have_text(
        ["-2.5", "0.5", "10"]
    )
    extra_table.get_by_role("button", name="Name").click()
    expect(extra_table.locator("tbody td:first-child")).to_have_text(
        ["Item 1", "Item 2", "Item 10"]
    )
    expect(extra_table.get_by_role("link", name="Item 10")).to_have_attribute(
        "href", "#tables"
    )
    page.locator(".lumina-table-panel").first.get_by_role("searchbox").fill("guide")
    expect(extra_table.locator("tbody tr:visible")).to_have_count(3)
    expect(page.locator('[id^="unsupported-"] .lumina-table-sort')).to_have_count(0)


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_toc_scrollspy(page: Page, live_server: str, theme):
    """The curved guide follows nesting, wrapped labels, and the active section."""
    page.set_viewport_size({"width": 390, "height": 900})
    page.goto(f"{live_server}/guides/navigation.html")
    page.evaluate("theme => document.documentElement.dataset.theme = theme", theme)
    page.set_viewport_size({"width": 1400, "height": 900})
    nav = page.locator(".lumina-toc-nav")
    guide = nav.locator(".lumina-toc-guide")
    expect(guide).to_have_attribute("aria-hidden", "true")
    page.evaluate("document.fonts.ready")

    nested = nav.locator('a[href="#dropdown-menus"]')
    nested.click()
    expect(nested).to_have_attribute("aria-current", "location")
    expect(nav.locator("a.lumina-toc-active")).to_have_count(1)
    page.wait_for_function("""() => {
        const nav = document.querySelector('.lumina-toc-nav');
        return getComputedStyle(nav.querySelector('circle')).fill
            === getComputedStyle(nav.querySelector('[aria-current]')).color;
    }""")
    assert (
        guide.locator(".lumina-toc-indicator").evaluate(
            "el => getComputedStyle(el).clipPath"
        )
        != "none"
    )

    # Narrowing the outline wraps labels; the guide must track the new geometry.
    for width in (220, 180):
        page.locator(".lumina-toc-container").evaluate(
            "(el, width) => el.style.width = `${width}px`", width
        )
        page.wait_for_function("""() => {
            const nav = document.querySelector('.lumina-toc-nav');
            const links = [...nav.querySelectorAll('a')].filter(el => el.offsetHeight);
            const path = nav.querySelector('.lumina-toc-track');
            const end = path.getPointAtLength(path.getTotalLength());
            const last = links.at(-1);
            const active = nav.querySelector('[aria-current]');
            const dot = nav.querySelector('circle');
            return Math.abs(end.y - last.offsetTop - last.offsetHeight) < 1
                && Number(dot.getAttribute('cx')) === active.offsetLeft + 1
                && Number(dot.getAttribute('cy')) === active.offsetTop + active.offsetHeight / 2;
        }""")
    assert " C " in guide.locator("path").first.get_attribute("d")
    parent = nav.locator('a[href="#header-navigation-links"]')
    assert nested.bounding_box()["x"] > parent.bounding_box()["x"]
    nested.focus()
    expect(nested).to_be_focused()


def test_toc_tracks_reading_position(page: Page, live_server: str):
    """Nested sections track the reading line in both directions and after jumps."""
    page.set_viewport_size({"width": 1400, "height": 900})
    page.emulate_media(reduced_motion="reduce")
    page.goto(f"{live_server}/guides/navigation.html")
    page.evaluate("document.fonts.ready")
    active = page.locator('.lumina-toc-nav a[aria-current="location"]')
    parent = "collapsible-sidebar-items"
    child = "marking-a-branch-collapsed-by-default"

    for header_height in (56, 128):
        page.evaluate(
            """height => {
            document.documentElement.style.setProperty('--lumina-header-offset', `${height}px`);
            document.querySelector('header').style.height = `${height}px`;
        }""",
            header_height,
        )
        # WebKit can expose the old section geometry until the new header
        # spacing has been resolved. Measure only after the layout catches up.
        expect(page.locator(".lumina-wrapper")).to_have_css(
            "margin-top", f"{header_height}px"
        )
        # Cross each boundary downwards and upwards, including a large jump.
        for target, delta, expected in [
            ("sidebar-depth", 0, "sidebar-depth"),
            (parent, -24, "sidebar-depth"),
            (parent, 24, parent),
            (child, -24, parent),
            (child, 24, child),
            (child, -24, parent),
            (parent, -24, "sidebar-depth"),
            ("breadcrumbs", 24, "breadcrumbs"),
            (parent, 24, parent),
        ]:
            page.evaluate(
                """([id, delta]) => {
                const target = document.getElementById(id);
                window.scrollTo({top: scrollY + target.getBoundingClientRect().top
                    - parseFloat(getComputedStyle(target).scrollMarginTop) + delta,
                    behavior: 'instant'});
            }""",
                [target, delta],
            )
            expect(active).to_have_attribute("href", f"#{expected}")

    page.goto(f"{live_server}/guides/navigation.html#{child}")
    expect(active).to_have_attribute("href", f"#{child}")
    page.reload()
    expect(active).to_have_attribute("href", f"#{child}")
    page.evaluate(
        "window.scrollTo({top: document.documentElement.scrollHeight, behavior: 'instant'})"
    )
    last = page.locator(".lumina-toc-nav a").last
    expect(last).to_have_attribute("aria-current", "location")
    page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
    expect(active).to_have_attribute("href", "#header-navigation-links")


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
def test_reading_chrome(page: Page, live_server: str, theme: str, browser_name: str):
    """Shared reading layout works beyond the original installation preview."""
    page.emulate_media(reduced_motion="reduce")
    page.add_init_script(f"localStorage.setItem('lumina-theme', '{theme}')")
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.goto(f"{live_server}/guides/search.html")
    expect(page.locator(".lumina-article")).to_have_css("font-size", "16px")
    expect(page.locator(".lumina-article h1")).to_have_css("font-size", "40px")
    reading_time = page.locator(".lumina-article h1 + p + .lumina-reading-time")
    expect(reading_time).to_be_visible()
    expect(reading_time.locator("svg")).to_be_visible()
    expect(page.locator(".lumina-page-actions .lumina-reading-time")).to_have_count(0)
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
    trigger.focus()
    page.keyboard.press(
        "Alt+Tab" if browser_name == "webkit" and sys.platform == "darwin" else "Tab"
    )
    expect(menu.locator("a").first).to_be_focused()
    page.keyboard.press("Escape")
    expect(menu).to_be_hidden()
    expect(trigger).to_be_focused()
    assert page.locator(".lumina-sidebar-desktop .is-collapsed").count() >= 2

    actions = page.locator(".lumina-page-actions")
    actions.locator("summary").press("Enter")
    expect(actions.get_by_role("button", name="Copy page as Markdown")).to_be_visible()
    expect(actions.get_by_role("link", name="Edit this page")).to_be_visible()
    if browser_name == "chromium":
        page.context.grant_permissions(["clipboard-read", "clipboard-write"])
    else:
        page.evaluate("""() => {
            navigator.clipboard.writeText = async text => { window.copiedMarkdown = text; };
        }""")
    actions.get_by_role("button", name="Copy page as Markdown").press("Enter")
    expect(actions.locator("button")).to_contain_text("Copied!")
    markdown = page.evaluate(
        "navigator.clipboard.readText()"
        if browser_name == "chromium"
        else "window.copiedMarkdown"
    )
    assert "# Search" in markdown
    assert "min read" not in markdown
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


def test_mermaid_sizing_and_colors_survive_theme_changes(page: Page, live_server: str):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"{live_server}/reference/diagrams.html")
    diagrams = page.locator(".lumina-article pre.mermaid > svg")
    expect(diagrams).to_have_count(12, timeout=60000)
    page.set_viewport_size({"width": 1440, "height": 1000})

    for theme in ("dark", "light"):
        page.evaluate("theme => document.documentElement.dataset.theme = theme", theme)
        page.wait_for_function(
            """() => {
                const diagrams = [...document.querySelectorAll('.lumina-article pre.mermaid > svg')];
                return diagrams.length === 12 && diagrams.every(svg =>
                    svg.style.getPropertyValue('--lumina-diagram-width') &&
                    svg.getBoundingClientRect().width <= svg.viewBox.baseVal.width + 1);
            }"""
        )
        label = diagrams.first.locator(".nodeLabel").first
        expect(label).to_have_css("font-family", '"Source Sans 3", sans-serif')
        # The author's classDef highlight survives the theme defaults.
        highlight = diagrams.first.locator(".node.ready path, .node.ready rect").first
        expect(highlight).to_have_css("stroke-width", "2px")
        page.locator(".mermaid-fullscreen-btn").first.click()
        viewer = page.locator(".mermaid-fullscreen-modal.active")
        expect(viewer).to_be_visible()
        expect(viewer.locator("svg")).to_be_visible()
        page.keyboard.press("Escape")
        expect(viewer).to_have_count(0)

    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    assert diagrams.evaluate_all(
        "svgs => svgs.every(svg => svg.getBoundingClientRect().width <= svg.parentElement.clientWidth)"
    )
    assert not errors


def test_search_scopes_and_heading_links(page: Page, live_server: str):
    """Real Pagefind filters exclude other sections and link to actual headings."""
    page.click("[data-search-trigger]")
    modal = page.locator("#lumina-search-modal")
    scope = modal.get_by_label("Search in")
    expect(scope).to_be_visible()
    scope.select_option(label="Developer Documentation")
    modal.get_by_role("searchbox").fill("search")
    links = modal.locator("[data-search-result]")
    expect(links.first).to_be_visible()
    for href in links.evaluate_all("els => els.map(el => el.getAttribute('href'))"):
        assert "/contributing/" in href
    expect(modal.get_by_text("Contributing", exact=True).first).to_be_visible()
    heading = modal.locator('[data-search-result][href*="#"]').first
    expect(heading).to_be_visible()
    href = heading.get_attribute("href")
    heading.click()
    expect(page).to_have_url(live_server + href)
    assert page.evaluate(
        "!!document.getElementById(decodeURIComponent(location.hash.slice(1)))"
    )


def test_search_scoped_empty_state_and_reset(page: Page):
    page.click("[data-search-trigger]")
    modal = page.locator("#lumina-search-modal")
    scope = modal.get_by_label("Search in")
    scope.select_option(label="Developer Documentation")
    search = modal.get_by_role("searchbox")
    search.fill("petstore")
    expect(modal.get_by_text("No results in Developer Documentation.")).to_be_visible()
    modal.get_by_role("button", name="Search all docs").click()
    expect(search).to_have_value("petstore")
    expect(scope).to_have_value("")
    expect(modal.locator("[data-search-result]").first).to_be_visible()
    scope.select_option(label="Developer Documentation")
    expect(modal.get_by_text("No results in Developer Documentation.")).to_be_visible()
    search.focus()
    page.keyboard.press("Escape")
    page.click("[data-search-trigger]")
    expect(scope).to_have_value("")


def test_search_ignores_stale_scope_and_query_responses(page: Page):
    """Old responses, including errors, cannot replace a newer cached result."""
    page.click("[data-search-trigger]")
    expect(page.get_by_label("Search in")).to_be_visible()
    outcome = page.evaluate("""async () => {
        const state = Alpine.$data(document.querySelector('#lumina-search-modal'));
        const pending = [];
        state.pagefind = {search: () => new Promise((resolve, reject) => pending.push({resolve, reject}))};
        const response = title => ({results: [{data: async () => ({url: '/' + title, meta: {title}, excerpt: title})}]});
        state.query = 'same';
        state.scope = 'User Documentation';
        const old = state.search();
        state.scope = 'Developer Documentation';
        const current = state.search();
        pending[1].resolve(response('current'));
        await current;
        pending[0].resolve(response('stale'));
        await old;
        const scoped = state.results[0].title;
        state.query = 'older';
        const failed = state.search();
        state.query = 'same';
        await state.search(); // cached scoped result
        pending[2].reject(new Error('late failure'));
        await failed;
        const cached = state.results[0].title;
        state.query = 'clear';
        const clear = state.search();
        state.query = '';
        await state.search();
        pending[3].resolve(response('stale'));
        await clear;
        return {scoped, cached, results: state.results.length, error: state.error};
    }""")
    assert outcome == {
        "scoped": "current",
        "cached": "current",
        "results": 0,
        "error": None,
    }


def test_search_fallback_when_pagefind_unavailable(page: Page):
    page.route("**/_pagefind/**", lambda route: route.abort())
    page.click("[data-search-trigger]")
    modal = page.locator("#lumina-search-modal")
    modal.get_by_role("searchbox").fill("hello world")
    fallback = modal.get_by_role("link", name='Search for "hello world"')
    expect(fallback).to_have_attribute("href", "./search.html?q=hello%20world")
    expect(modal.get_by_label("Search in")).to_have_count(0)


def test_search_keyboard_reaches_heading(page: Page, live_server: str):
    page.click("[data-search-trigger]")
    modal = page.locator("#lumina-search-modal")
    search = modal.get_by_role("searchbox")
    search.fill("pagefind")
    links = modal.locator("[data-search-result]")
    expect(links.first).to_be_visible()
    hrefs = links.evaluate_all("els => els.map(el => el.getAttribute('href'))")
    index = next(i for i, href in enumerate(hrefs) if "#" in href)
    for _ in range(index):
        search.press("ArrowDown")
    search.press("Enter")
    expect(page).to_have_url(live_server + hrefs[index])
