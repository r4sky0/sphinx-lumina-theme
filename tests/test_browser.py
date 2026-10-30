"""Browser-based tests using Playwright."""

import base64
import re
import sys

import pytest
from conftest import (
    HTTP_ENDPOINT_RST,
    HTTPDOMAIN_TRANSLATED_CONF,
    build_translated_site,
    sphinx_app,
)
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True)
def _goto_index(page: Page, live_server: str):
    """Navigate to the site index before each test."""
    page.goto(live_server)
    page.wait_for_function("() => window.Alpine !== undefined")


def test_accent_preview(page: Page, live_server: str):
    """The documentation-only accent picker previews theme colors."""
    page.goto(f"{live_server}/getting-started/configuration.html#accent-colors")
    picker = page.get_by_role("group", name="Preview accent color")
    blue = picker.get_by_role("button", name="Blue #3b82f6")
    orange = picker.get_by_role("button", name="Burnt Orange #ea580c")
    emerald = picker.get_by_role("button", name="Emerald #10b981")
    root = page.locator("html")
    sidebar_link = page.locator(".lumina-sidebar-nav a.current").first

    expect(emerald).to_have_attribute("aria-pressed", "true")
    for mode in ("light", "dark"):
        root.evaluate("(element, value) => element.dataset.theme = value", mode)
        original_link = root.evaluate(
            "element => getComputedStyle(element).getPropertyValue('--lumina-link')"
        )
        original_sidebar = sidebar_link.evaluate(
            "element => getComputedStyle(element).color"
        )
        blue.click()
        expect(root).to_have_attribute("data-accent-preview", "")
        expect(blue).to_have_attribute("aria-pressed", "true")
        assert (
            root.evaluate(
                "element => getComputedStyle(element).getPropertyValue('--lumina-accent').trim()"
            )
            == "#3b82f6"
        )
        assert (
            root.evaluate(
                "element => getComputedStyle(element).getPropertyValue('--lumina-link')"
            )
            != original_link
        )
        assert (
            sidebar_link.evaluate("element => getComputedStyle(element).color")
            != original_sidebar
        )
        expect(page.locator("#accent-preview p")).to_contain_text(
            '"accent_color": "#3b82f6"'
        )
        orange.click()
        expect(orange).to_have_attribute("aria-pressed", "true")
        expect(root).to_have_css("--lumina-accent", "#ea580c")
        expect(page.locator("#accent-preview p")).to_contain_text(
            '"accent_color": "#ea580c"'
        )
        emerald.click()
        expect(root).not_to_have_attribute("data-accent-preview", "")
        expect(emerald).to_have_attribute("aria-pressed", "true")

    blue.click()
    page.reload()
    expect(root).not_to_have_attribute("data-accent-preview", "")
    expect(emerald).to_have_attribute("aria-pressed", "true")


def test_font_preview(page: Page, live_server: str):
    """The documentation-only font picker previews the font tokens."""
    page.goto(f"{live_server}/guides/custom-styling.html#preview-a-font")
    body_group = page.get_by_role("group", name="Body text")
    code_group = page.get_by_role("group", name="Code")
    default = body_group.get_by_role("button", name="Source Sans 3")
    literata = body_group.get_by_role("button", name="Literata")
    fira_code = code_group.get_by_role("button", name="Fira Code")
    body = page.locator("body")
    code = page.locator(".lumina-article code").first
    # Browsers differ on quoting family names when serializing font-family.
    fira_code_stack = re.compile(r'^"?Fira Code"?, ')

    expect(default).to_have_attribute("aria-pressed", "true")
    default_body_font = body.evaluate("element => getComputedStyle(element).fontFamily")

    with page.expect_response("**/_static/fonts/literata.woff2") as response:
        literata.click()
    assert response.value.ok
    expect(literata).to_have_attribute("aria-pressed", "true")
    expect(body).to_have_css("font-family", "Literata, Georgia, serif")
    expect(page.locator("#font-preview")).to_contain_text(
        "--lumina-font-sans: Literata, Georgia, serif"
    )

    fira_code.click()
    expect(code).to_have_css("font-family", fira_code_stack)
    expect(body).to_have_css("font-family", "Literata, Georgia, serif")

    default.click()
    expect(body).to_have_css("font-family", default_body_font)

    page.reload()
    expect(code).not_to_have_css("font-family", fira_code_stack)
    expect(default).to_have_attribute("aria-pressed", "true")


def test_rtl_layout_mirrors(page: Page, rtl_server: str):
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(f"{rtl_server}/typography-test.html")

    sidebar = page.locator("#lumina-sidebar").bounding_box()
    content = page.locator("#lumina-content").bounding_box()
    assert sidebar["x"] > content["x"]

    nav = page.locator(".lumina-toc-nav").bounding_box()
    dot = page.locator(".lumina-toc-guide circle").bounding_box()
    assert dot["x"] > nav["x"] + nav["width"] / 2

    assert page.evaluate("document.documentElement.scrollWidth === innerWidth")
    expect(page.locator("footer nav .inline-block").first).to_have_css("scale", "-1 1")

    page.goto(f"{rtl_server}/index.html")
    code = page.locator("div.highlight pre").first
    expect(code).to_have_css("direction", "ltr")
    expect(code).to_have_css("font-family", re.compile(r"JetBrains Mono.*Arial"))


def test_rtl_mobile_drawer_opens_from_the_right(page: Page, rtl_server: str):
    page.set_viewport_size({"width": 390, "height": 800})
    page.goto(f"{rtl_server}/typography-test.html")
    page.locator("[aria-controls='lumina-sidebar-drawer']").click()

    drawer = page.locator("#lumina-sidebar-drawer")
    expect(drawer).to_be_visible()
    page.wait_for_timeout(400)
    box = drawer.bounding_box()
    assert box["x"] + box["width"] == 390


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


def test_fluid_without_offscreen_canvas(context, live_server: str):
    page = context.new_page()
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


@pytest.mark.parametrize("width", [390, 1440])
def test_hero_text_has_no_entrance_animation(page: Page, width):
    page.set_viewport_size({"width": width, "height": 844})
    for selector in ("title", "subtitle", "actions", "tags"):
        assert (
            page.locator(f".lumina-hero-{selector}").evaluate(
                "el => getComputedStyle(el).animationName"
            )
            == "none"
        )


def test_headerlink_is_spaced_from_heading_text(page: Page, live_server: str):
    page.goto(f"{live_server}/getting-started/configuration.html")
    gap = page.locator("h2 > a.headerlink").first.evaluate(
        """link => {
            const range = document.createRange();
            range.selectNodeContents(link.parentElement.firstChild);
            return link.getBoundingClientRect().left - range.getBoundingClientRect().right;
        }"""
    )
    assert gap > 0


def test_landing_without_hero_clears_header(page: Page):
    """Landing content starts below the fixed header when no hero is present."""
    page.locator(".lumina-hero").evaluate("el => el.remove()")
    # The docs index body is empty and hidden; unhide it to measure the layout.
    page.locator("#lumina-content").evaluate("el => el.classList.remove('is-empty')")
    header_bottom = page.locator("#lumina-header header").evaluate(
        "el => el.getBoundingClientRect().bottom"
    )
    content_top = page.locator("#lumina-content .lumina-article").evaluate(
        "el => el.getBoundingClientRect().top"
    )
    assert content_top >= header_bottom


def test_font_subsets_load_full_fonts_only_for_other_characters(page: Page):
    page.evaluate("document.fonts.ready")
    font_urls = "performance.getEntriesByType('resource').map(r => r.name).filter(n => n.endsWith('.woff2'))"
    render = """async ({font, text}) => {
        const p = document.createElement('p');
        p.style.font = font;
        p.textContent = text;
        document.body.prepend(p);
        p.getBoundingClientRect();
        await document.fonts.ready;
    }"""
    assert all(url.endswith("-latin.woff2") for url in page.evaluate(font_urls))
    for family, weights in (
        ("Source Sans 3", (400, 500, 600, 700)),
        ("JetBrains Mono", (400, 500)),
    ):
        for weight in weights:
            font = f'{weight} 16px "{family}"'
            page.evaluate(render, {"font": font, "text": "Café Cafe\u0301 → ⌘"})
            assert all(url.endswith("-latin.woff2") for url in page.evaluate(font_urls))
    for family, stem in (
        ("Source Sans 3", "source-sans-3"),
        ("JetBrains Mono", "jetbrains-mono"),
    ):
        page.evaluate(render, {"font": f'16px "{family}"', "text": "Ελληνικά Русский"})
        assert any(
            url.endswith(f"/{stem}-regular.woff2") for url in page.evaluate(font_urls)
        )


def test_search_returns_results(page: Page, live_server: str):
    """Typing a query should produce Pagefind results."""
    expect(page.locator('meta[name="lumina-search-backend"]')).to_have_attribute(
        "content", "pagefind"
    )
    page.click("[data-search-trigger]")
    page.locator("#lumina-search-modal input[type='search']").fill("getting started")
    page.wait_for_selector("#lumina-search-modal a[href]", timeout=10000)
    results = page.locator("#lumina-search-modal a[href]")
    assert results.count() >= 1
    expect(results.first).not_to_have_attribute("href", re.compile(r"search\.html"))


def test_sphinx_search_backend(page: Page, sphinx_search_server: str):
    """The Sphinx backend links the modal to Sphinx's search page, never Pagefind."""
    requests = []
    page.on("request", lambda request: requests.append(request.url))
    page.goto(f"{sphinx_search_server}/index.html")
    page.wait_for_function("() => window.Alpine !== undefined")
    expect(page.locator('meta[name="lumina-search-backend"]')).to_have_attribute(
        "content", "sphinx"
    )

    page.click("[data-search-trigger]")
    modal = page.locator("#lumina-search-modal")
    modal.get_by_role("searchbox").fill("content")
    modal.get_by_role("link", name='Search for "content"').click()
    expect(page.locator("#search-results li").first).to_be_visible()
    assert not [url for url in requests if "_pagefind" in url]


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
        (1440, 700),
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
    page.wait_for_function("""() => {
        const root = document.documentElement;
        return parseFloat(root.style.getPropertyValue('--lumina-announcement-height'))
            === document.querySelector('#lumina-announcement').getBoundingClientRect().height;
    }""")
    # Check the cover with the announcement visible, then dismissed below.
    assert page.evaluate(
        "() => document.documentElement.scrollHeight <= innerHeight"
        " && document.documentElement.scrollWidth <= innerWidth"
    )
    expect(page.locator(".lumina-hero-btn-primary")).to_be_in_viewport()
    expect(page.locator(".lumina-hero-tags")).to_be_in_viewport()
    page.get_by_role("button", name="Dismiss announcement").click()
    assert page.evaluate("document.documentElement.scrollHeight <= innerHeight")


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
    expect(page.locator(".lumina-article p").first).to_have_css("hyphens", "manual")
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


def test_sidebar_expands_only_current_path(page: Page, live_server: str):
    """Like Sphinx's default toctree, branches off the current path start collapsed."""
    page.goto(f"{live_server}/getting-started/installation.html")
    branches = page.locator(".lumina-sidebar-desktop li.has-children").evaluate_all(
        """items => items.map(li => [
            li.classList.contains("current") || !!li.querySelector(".current"),
            li.classList.contains("is-collapsed"),
        ])"""
    )
    assert [True, False] in branches
    assert [False, True] in branches
    assert all(current != collapsed for current, collapsed in branches)


@pytest.mark.parametrize("width", [390, 1440])
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_sidebar_row_alignment(page: Page, live_server: str, width, theme):
    """Arrows and active labels stay centered, including wrapped menu labels."""
    page.set_viewport_size({"width": width, "height": 844})
    page.goto(f"{live_server}/getting-started/installation.html")
    page.evaluate("theme => document.documentElement.dataset.theme = theme", theme)
    if width < 1024:
        page.locator("[data-sidebar-toggle]").click()
        sidebar = page.locator("#lumina-sidebar-drawer")
    else:
        sidebar = page.locator(".lumina-sidebar-desktop")
    expect(sidebar).to_be_visible()
    page.evaluate("document.fonts.ready")
    for wrapped in (False, True):
        if wrapped:
            sidebar.locator("li.has-children > a").first.evaluate(
                "a => a.textContent = 'Getting started with installation and configuration'"
            )
        offsets = sidebar.locator(".lumina-sidebar-nav-toggle:visible").evaluate_all(
            """buttons => buttons.map(button => {
                const link = button.previousElementSibling.getBoundingClientRect();
                const arrow = button.getBoundingClientRect();
                return Math.abs(arrow.y + arrow.height / 2 - link.y - link.height / 2);
            })"""
        )
        assert offsets and max(offsets) < 1
    highlight_gap = sidebar.locator("a.current").evaluate(
        """link => {
            const box = link.getBoundingClientRect();
            const range = document.createRange();
            range.selectNodeContents(link);
            const text = range.getBoundingClientRect();
            return Math.abs((text.top - box.top) - (box.bottom - text.bottom));
        }"""
    )
    assert highlight_gap < 2


@pytest.mark.parametrize("width", [390, 1440])
def test_navigation_wraps_long_names(page: Page, live_server: str, width):
    """Names without spaces, like Java packages, wrap inside sidebar and TOC links."""
    page.set_viewport_size({"width": width, "height": 844})
    page.goto(f"{live_server}/getting-started/installation.html")
    if width < 1024:
        page.locator("[data-sidebar-toggle]").click()
        links = [page.locator("#lumina-sidebar-drawer li.has-children > a").first]
    else:
        links = [
            page.locator(".lumina-sidebar-desktop li.has-children > a").first,
            page.locator(".lumina-toc-nav a:visible").first,
        ]
    for link in links:
        expect(link).to_be_visible()
        overflow = link.evaluate(
            """a => {
                a.textContent = 'org.apache.commons.lang3.concurrent.locks.LockingVisitors';
                return a.scrollWidth - a.clientWidth;
            }"""
        )
        assert overflow <= 0


@pytest.mark.parametrize("path", ["index.html", "getting-started/installation.html"])
def test_mobile_announcement_reserves_space_before_alpine(
    page: Page, live_server: str, path
):
    """A wrapped banner must reserve its full height before deferred JS loads."""
    page.set_viewport_size({"width": 390, "height": 844})
    page.route("**/lumina.js*", lambda route: route.abort())
    page.goto(f"{live_server}/{path}")
    heights = page.locator("#lumina-announcement").evaluate(
        """banner => ({
            actual: banner.getBoundingClientRect().height,
            reserved: parseFloat(document.documentElement.style.getPropertyValue(
                '--lumina-announcement-height')),
        })"""
    )
    assert heights["actual"] > 36
    # The fallback font can differ by one pixel before the webfont finishes loading.
    assert abs(heights["reserved"] - heights["actual"]) <= 1


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


def test_mobile_stacked_table_caption_and_stub_column(page: Page, live_server: str):
    """Stacked tables keep a full-width caption and title each card with its row header."""
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(f"{live_server}/reference/lists-and-tables.html")
    page.wait_for_function("() => window.Alpine !== undefined")

    table = page.locator(
        "table.lumina-table-stackable",
        has=page.locator("caption", has_text="Theme Comparison"),
    )
    expect(table).to_be_visible()
    layout = table.evaluate(
        """(table) => {
            const width = (el) => el.getBoundingClientRect().width;
            const row = table.tBodies[0].rows[0];
            return {
                table: width(table),
                caption: width(table.caption),
                row: row.clientWidth,
                stub: width(row.querySelector("th")),
            };
        }"""
    )
    assert layout["caption"] >= layout["table"] - 1
    # The stub spans the card's content box (row width minus its padding).
    assert layout["stub"] >= layout["row"] - 2 * 12 - 1


@pytest.mark.parametrize("width", [390, 1440])
def test_interactive_tables(context, live_server: str, width):
    """Opt-in tables filter independently and support keyboard sorting/reset."""
    # A fresh page, so errors from the landing page's fluid worker (started by
    # the autouse index visit) cannot leak into this page's error log.
    page = context.new_page()
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


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("motion", ["no-preference", "reduce"])
def test_toc_indicator_stays_aligned_during_fast_scroll(
    page: Page, live_server: str, theme, motion
):
    """The snake animates without splitting, including fast direction changes."""
    page.set_viewport_size({"width": 1400, "height": 900})
    page.emulate_media(reduced_motion=motion)
    page.goto(f"{live_server}/guides/navigation.html")
    page.evaluate("theme => document.documentElement.dataset.theme = theme", theme)
    page.evaluate("document.fonts.ready")
    expect(page.locator(".lumina-toc-guide")).to_be_visible()

    samples = page.evaluate(r"""async () => {
        const nav = document.querySelector('.lumina-toc-nav');
        const indicator = nav.querySelector('.lumina-toc-indicator');
        const dot = nav.querySelector('circle');
        const links = [...nav.querySelectorAll('a')].filter(el => el.offsetHeight);
        const samples = [];
        for (const link of [...links, ...links.toReversed()]) {
            const target = document.getElementById(link.hash.slice(1));
            window.scrollTo({top: scrollY + target.getBoundingClientRect().top
                - parseFloat(getComputedStyle(target).scrollMarginTop) + 2,
                behavior: 'instant'});
            await new Promise(requestAnimationFrame);
            await new Promise(requestAnimationFrame);
            const active = nav.querySelector('[aria-current]');
            const bounds = getComputedStyle(indicator).clipPath.split(',');
            const top = parseFloat(bounds[1].trim().split(/\s+/)[1]);
            const bottom = parseFloat(bounds[2].trim().split(/\s+/)[1]);
            samples.push({
                href: active.hash,
                top,
                bottom,
                expectedTop: active.offsetTop,
                expectedBottom: active.offsetTop + active.offsetHeight,
                dotY: Number(dot.getAttribute('cy')),
                onGuide: nav.querySelector('.lumina-toc-track').isPointInStroke(
                    new DOMPoint(Number(dot.getAttribute('cx')), Number(dot.getAttribute('cy')))),
            });
        }
        return samples;
    }""")
    assert len({sample["href"] for sample in samples}) > 3
    for sample in samples:
        assert sample["onGuide"], sample
        assert sample["bottom"] > sample["top"], sample
        assert sample["dotY"] == pytest.approx(
            (sample["top"] + sample["bottom"]) / 2, abs=0.1
        ), sample
    in_motion = [
        sample for sample in samples if abs(sample["top"] - sample["expectedTop"]) > 1
    ]
    assert bool(in_motion) == (motion == "no-preference")
    page.wait_for_function(r"""() => {
        const nav = document.querySelector('.lumina-toc-nav');
        const active = nav.querySelector('[aria-current]');
        const clip = getComputedStyle(nav.querySelector('.lumina-toc-indicator')).clipPath;
        const top = parseFloat(clip.split(',')[1].trim().split(/\s+/)[1]);
        const dot = nav.querySelector('circle');
        return Math.abs(top - active.offsetTop) < 0.1
            && Number(dot.getAttribute('cx')) === active.offsetLeft + 1
            && Number(dot.getAttribute('cy')) === active.offsetTop + active.offsetHeight / 2;
    }""")


@pytest.mark.parametrize("header_height", [56, 128])
def test_toc_tracks_reading_position(page: Page, live_server: str, header_height):
    """Nested sections track the reading line in both directions and after jumps."""
    page.set_viewport_size({"width": 1400, "height": 900})
    page.emulate_media(reduced_motion="reduce")
    # Apply the header size before every load, so deep links and reloads see it too.
    page.add_init_script(f"""
        const sheet = new CSSStyleSheet();
        sheet.replaceSync(':root {{ --lumina-header-offset: {header_height}px !important; }}'
            + 'header {{ height: {header_height}px !important; }}');
        document.adoptedStyleSheets = [sheet];
    """)
    page.goto(f"{live_server}/guides/navigation.html")
    page.evaluate("document.fonts.ready")
    expect(page.locator(".lumina-wrapper")).to_have_css(
        "margin-top", f"{header_height}px"
    )
    active = page.locator('.lumina-toc-nav a[aria-current="location"]')
    parent = "doc-sections"
    child = "setup"

    # Cross each boundary downwards and upwards, including a large jump.
    for target, delta, expected in [
        ("previous-next-navigation", 0, "previous-next-navigation"),
        (parent, -24, "previous-next-navigation"),
        (parent, 24, parent),
        (child, -24, parent),
        (child, 24, child),
        (child, -24, parent),
        (parent, -24, "previous-next-navigation"),
        ("version-switcher", 24, "version-switcher"),
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


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_announcement_layout(page: Page, live_server: str, theme: str):
    """Wrapped announcements must clear content and navigation at every size."""
    page.goto(f"{live_server}/guides/navigation.html")
    page.evaluate("theme => document.documentElement.dataset.theme = theme", theme)
    page.evaluate("document.fonts.ready")
    banner = page.locator("#lumina-announcement")
    expect(banner).to_be_visible()
    for width, height in ((1440, 900), (768, 1024), (390, 844), (320, 568), (844, 390)):
        page.set_viewport_size({"width": width, "height": height})
        page.wait_for_function("""() => {
            const header = document.querySelector('#lumina-header header');
            const wrapper = document.querySelector('.lumina-wrapper');
            return Math.abs(wrapper.getBoundingClientRect().top - header.clientHeight) <= 1;
        }""")
        breadcrumb = page.get_by_role("navigation", name="Breadcrumb", exact=True)
        header_bottom = page.locator("#lumina-header header").bounding_box()["height"]
        assert breadcrumb.bounding_box()["y"] >= header_bottom
        # Visibility alone does not detect a fixed header covering the link.
        breadcrumb.get_by_role("link").first.click(trial=True)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        if width < 1024:
            page.get_by_role("button", name="Toggle navigation").click()
            drawer = page.locator("#lumina-sidebar-drawer")
            expect(drawer).to_be_visible()
            assert abs(drawer.bounding_box()["y"] - header_bottom) <= 1
            page.keyboard.press("Escape")
            expect(drawer).to_be_hidden()
        else:
            sidebar = page.locator(".lumina-sidebar-desktop").bounding_box()
            assert abs(sidebar["y"] + sidebar["height"] - height) <= 1

    page.get_by_role("button", name="Dismiss announcement").click()
    expect(banner).to_be_hidden()
    page.reload()
    expect(banner).to_be_hidden()
    assert page.locator(".lumina-wrapper").bounding_box()["y"] == 56
    page.get_by_role("navigation", name="Breadcrumb", exact=True).get_by_role(
        "link"
    ).first.click()
    expect(page).to_have_url(f"{live_server}/guides/index.html")


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


def test_mermaid_sizing_and_colors_survive_theme_changes(context, live_server: str):
    page = context.new_page()
    page.route("https://cdn.jsdelivr.net/**", lambda route: route.abort())
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
        expect(label).to_have_css(
            "font-family",
            '"Source Sans 3", "Source Sans 3 Fallback", "Source Sans Pro", '
            "system-ui, -apple-system, sans-serif",
        )
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


def test_sphinx_search_page_lists_results(page: Page, live_server: str):
    """The fallback search page runs Sphinx's search after deferred scripts load."""
    # Leave the index first: WebKit reports its cancelled hero worker as a page error.
    page.goto("about:blank")
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"{live_server}/search.html?q=pagefind")
    expect(page.locator("#search-results li").first).to_be_visible()
    assert errors == []

    form = page.locator(".lumina-search-page-form")
    field = form.locator("input[name='q']")
    expect(field).to_have_value("pagefind")
    expect(form.locator(".lumina-search-page-field")).to_have_css(
        "border-top-style", "solid"
    )
    field.fill("sidebar")
    form.get_by_role("button", name="Search").click()
    expect(page).to_have_url(f"{live_server}/search.html?q=sidebar")
    expect(page.locator("#search-results li").first).to_be_visible()


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


def test_search_repeat_query_keeps_keyboard_selection(page: Page, live_server: str):
    """A repeated search for the shown query must not reset the selection."""
    page.click("[data-search-trigger]")
    modal = page.locator("#lumina-search-modal")
    search = modal.get_by_role("searchbox")
    search.fill("pagefind")
    links = modal.locator("[data-search-result]")
    expect(links.nth(1)).to_be_visible()
    hrefs = links.evaluate_all("els => els.map(el => el.getAttribute('href'))")
    search.press("ArrowDown")
    # Re-fire the debounced input search, as opening the modal does on a race.
    search.dispatch_event("input")
    page.wait_for_timeout(400)
    search.press("Enter")
    expect(page).to_have_url(live_server + hrefs[1])


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_search_keyboard_focus_indicators(page: Page, theme: str):
    page.emulate_media(reduced_motion="reduce")
    page.evaluate("theme => document.documentElement.dataset.theme = theme", theme)
    page.click("[data-search-trigger]")
    modal = page.locator("#lumina-search-modal")
    scope = modal.get_by_label("Search in")
    scope.select_option(label="User Documentation")
    search = modal.get_by_role("searchbox")
    search.fill("search")
    expect(modal.locator("[data-search-result]").first).to_be_visible()
    search.focus()
    search.press("Tab")
    expect(scope).to_be_focused()
    expect(scope).to_have_css("outline-width", "2px")
    expect(scope).to_have_css("outline-style", "solid")
    modal.locator("[data-search-result]").first.focus()
    expect(modal.locator("[data-search-result]").first).to_be_focused()
    expect(modal.locator("[data-search-result]").first).to_have_css(
        "outline-width", "2px"
    )


@pytest.mark.parametrize("width", [390, 1440])
def test_code_blocks_in_tables_scroll_inside_their_cell(
    page: Page, live_server: str, width: int
):
    """A long code line scrolls in its cell instead of widening the table."""
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(f"{live_server}/reference/lists-and-tables.html")
    page.wait_for_function("() => window.Alpine !== undefined")

    table = page.locator(".lumina-article table:has(pre)").first
    table.scroll_into_view_if_needed()
    sizes = table.evaluate("""table => {
        const article = document.querySelector('.lumina-article');
        const pres = [...table.querySelectorAll('pre')];
        return {
            table: table.getBoundingClientRect().right,
            article: article.getBoundingClientRect().right,
            page: document.documentElement.scrollWidth - innerWidth,
            scrolls: pres.some(pre => pre.scrollWidth > pre.clientWidth),
            narrowest: Math.min(...pres.map(pre => pre.clientWidth)),
        };
    }""")
    assert sizes["table"] <= sizes["article"] + 1
    # The code column keeps a usable width instead of collapsing.
    assert sizes["narrowest"] >= 200
    assert sizes["page"] <= 0
    assert sizes["scrolls"]


def test_code_wrap_toggle_takes_corner_without_copy_button(
    page: Page, live_server: str
):
    """The wrap toggle sits beside the copy button, or in the corner without one."""
    page.goto(f"{live_server}/reference/code-blocks.html")
    page.locator(".lumina-article div.highlight:has(> button.copybtn)").first.evaluate(
        "el => el.dataset.testBlock = ''"
    )
    block = page.locator("[data-test-block]")
    toggle = block.locator(":scope > .lumina-wrap-toggle")
    expect(toggle).to_have_count(1)

    def right_gap():
        return block.evaluate("""el => el.getBoundingClientRect().right
            - el.querySelector('.lumina-wrap-toggle').getBoundingClientRect().right""")

    beside_copy = right_gap()
    block.evaluate("el => el.querySelector(':scope > button.copybtn').remove()")
    assert right_gap() < beside_copy
    assert right_gap() <= 12


# ── Docutils body elements (Lumina drops Sphinx basic.css) ──

PIXEL = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)

DOCUTILS_INDEX = """\
Elements
========

.. sidebar:: Sidebar title

   Sidebar body.

.. topic:: Topic title

   Topic body.

.. rubric:: A rubric

.. centered:: Centered text

.. image:: pixel.png
   :align: right
   :width: 40px

Inline |pixel| image.

.. |pixel| image:: pixel.png

| Line one
|     Nested line

Term : classifier
   Definition.

.. versionremoved:: 1.0
   Gone.

.. productionlist::
   rule: "a" | "b"

.. math::
   :label: wide

   a + b

Footnote [#f]_.

.. [#f] The footnote.

=====  =========================
A      body row with several words
=====  =========================

Section
-------

Body.
"""


@pytest.fixture(scope="module")
def docutils_elements_page(tmp_path_factory):
    src = tmp_path_factory.mktemp("docutils_src")
    (src / "conf.py").write_text('project = "Elements"\nhtml_theme = "lumina"\n')
    (src / "index.rst").write_text(DOCUTILS_INDEX)
    (src / "pixel.png").write_bytes(PIXEL)
    out = tmp_path_factory.mktemp("docutils_build")
    sphinx_app(src, out).build()
    return (out / "index.html").as_uri()


def computed_style(
    page: Page, selector: str, prop: str, pseudo: str | None = None
) -> str:
    return page.locator(f".lumina-article {selector}").first.evaluate(
        "(el, [prop, pseudo]) => getComputedStyle(el, pseudo)[prop]", [prop, pseudo]
    )


def test_docutils_elements_are_styled(page: Page, docutils_elements_page: str):
    page.set_viewport_size({"width": 1280, "height": 900})
    page.goto(docutils_elements_page)

    assert computed_style(page, "aside.sidebar", "float") == "inline-end"
    assert computed_style(page, "img.align-right", "float") == "right"
    assert computed_style(page, "aside.topic", "borderTopStyle") == "solid"
    assert computed_style(page, "p.rubric", "fontWeight") == "600"
    assert computed_style(page, "p.centered", "textAlign") == "center"
    assert computed_style(page, "p img", "display") == "inline-block"
    assert computed_style(page, ".line-block .line-block", "marginLeft") != "0px"
    assert computed_style(page, "dt .classifier", "content", "::before") == '":"'
    assert computed_style(page, "div.versionremoved", "borderLeftStyle") == "solid"
    assert computed_style(page, "pre:has(> strong)", "overflowX") == "auto"
    assert (
        computed_style(page, "aside.footnote > span.label", "float") == "inline-start"
    )
    assert computed_style(page, "td", "hyphens") == "none"
    assert computed_style(page, "section > h2", "clear") == "both"


def test_floats_stack_on_narrow_screens(page: Page, docutils_elements_page: str):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(docutils_elements_page)

    assert computed_style(page, "aside.sidebar", "float") == "none"
    assert computed_style(page, "img.align-right", "float") == "none"


@pytest.mark.parametrize("width", [390, 1280])
def test_wide_math_scrolls_beside_its_number(
    page: Page, docutils_elements_page: str, width: int
):
    """A wide equation scrolls in its own box; its number stays visible beside it."""
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(docutils_elements_page)
    # Stand in for MathJax output so the check needs no network access.
    layout = page.locator(".lumina-article div.math").evaluate("""math => {
        const formula = document.createElement('mjx-container');
        formula.setAttribute('display', 'true');
        formula.style.display = 'block';
        formula.innerHTML = '<span style="display:inline-block;width:1500px;height:1em"></span>';
        [...math.childNodes].filter(n => n.nodeType === Node.TEXT_NODE).forEach(n => n.remove());
        math.append(formula);
        const box = formula.getBoundingClientRect();
        const number = math.querySelector('.eqno').getBoundingClientRect();
        return {
            page: document.documentElement.scrollWidth - innerWidth,
            scrolls: formula.scrollWidth > formula.clientWidth,
            numberAfterFormula: number.left >= box.right,
            numberInside: number.right <= math.getBoundingClientRect().right + 1,
        };
    }""")
    assert layout == {
        "page": 0,
        "scrolls": True,
        "numberAfterFormula": True,
        "numberInside": True,
    }


def test_search_lists_api_symbols_first(page: Page, live_server: str):
    """Domain objects match by qualified name and lead to their definitions."""
    page.click("[data-search-trigger]")
    modal = page.locator("#lumina-search-modal")
    search = modal.get_by_role("searchbox")
    search.fill("EventEmitter.on")
    first = modal.locator("[data-search-result]").first
    expect(first).to_contain_text("Python method in EventEmitter")
    expect(first).to_have_attribute("href", re.compile(r"#EventEmitter\.on$"))
    search.press("Enter")
    expect(page).to_have_url(re.compile(r"#EventEmitter\.on$"))

    # A symbol on the current page only changes the hash; the modal must close.
    page.click("[data-search-trigger]")
    search.fill("EventEmitter.emit")
    expect(modal.locator("[data-search-result]").first).to_have_attribute(
        "href", re.compile(r"#EventEmitter\.emit$")
    )
    search.press("Enter")
    expect(page).to_have_url(re.compile(r"#EventEmitter\.emit$"))
    expect(modal).not_to_have_attribute("open", "")


IN_PANEL = """([panel, link]) => {
  const box = document.querySelector(panel).getBoundingClientRect();
  const rect = document.querySelector(link).getBoundingClientRect();
  return rect.height > 0 && rect.top >= box.top && rect.bottom <= box.bottom;
}"""


def test_sidebar_and_toc_keep_current_entries_in_view(page: Page, live_server: str):
    """Panels taller than the viewport scroll to the current page and section."""
    page.emulate_media(reduced_motion="reduce")
    page.set_viewport_size({"width": 1280, "height": 360})
    page.goto(f"{live_server}/reference/typography.html")
    page.wait_for_function("() => window.Alpine !== undefined")
    sidebar = ".lumina-sidebar-desktop"
    assert page.locator(sidebar).evaluate("el => el.scrollTop") > 0
    current = f"{sidebar} a.current[href='#']"
    assert page.evaluate(IN_PANEL, [sidebar, current])

    toc = ".lumina-toc-scroll"
    assert page.locator(toc).evaluate("el => el.scrollHeight > el.clientHeight")
    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    page.wait_for_function(
        f"args => document.querySelector('{toc}').scrollTop > 0 && ({IN_PANEL})(args)",
        arg=[toc, ".lumina-toc-active"],
    )


@pytest.fixture(scope="module")
def spanish_page(tmp_path_factory):
    out = build_translated_site(
        tmp_path_factory.mktemp("i18n_es"),
        "es_ES",
        conf=HTTPDOMAIN_TRANSLATED_CONF,
        rst=HTTP_ENDPOINT_RST,
    )
    return (out / "index.html").as_uri()


def test_scripts_follow_the_page_language(page: Page, spanish_page: str):
    """Script-built text is translated, and the request editor reads translated fields."""
    page.goto(spanish_page)
    expect(page.locator(".lumina-wrap-toggle").first).to_have_attribute(
        "aria-label", "Ajustar las líneas largas"
    )
    page.get_by_role("button", name="Expandir todo").click()
    page.get_by_role("button", name="Probar").click()
    panel = page.locator(".lumina-try-it-panel")
    expect(panel.locator(".lumina-try-it-param-name", has_text="limit")).to_be_visible()
    expect(panel.get_by_label("Accept")).to_have_attribute(
        "placeholder", "application/json"
    )
