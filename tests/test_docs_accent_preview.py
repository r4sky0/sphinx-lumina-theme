"""The documentation-only accent picker previews theme colors."""

from playwright.sync_api import Page, expect


def test_accent_preview(page: Page, live_server: str):
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
