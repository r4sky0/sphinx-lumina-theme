"""HTTP endpoint layout and request controls across themes and screen sizes."""

import pytest
from playwright.sync_api import expect


@pytest.mark.parametrize("width", [390, 1440])
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_http_endpoint_controls(page, live_server, width, theme):
    page.set_viewport_size({"width": width, "height": 1000})
    page.add_init_script(
        "navigator.clipboard.writeText = async text => { window.copiedCurl = text; };"
    )
    page.route(
        "https://petstore3.swagger.io/**",
        lambda route: route.fulfill(
            json=[{"id": 1, "name": "Luna", "status": "available"}]
        ),
    )
    page.goto(f"{live_server}/reference/http-api.html")
    page.evaluate("theme => document.documentElement.dataset.theme = theme", theme)
    endpoint = page.locator("dl.http").first
    copy = endpoint.locator(".lumina-curl-copy")
    expect(copy).to_have_text("Copy curl")
    copy.click()
    expect(copy).to_have_text("Copied!")
    assert "/pet/findByStatus" in page.evaluate("window.copiedCurl")

    toggle = endpoint.get_by_role("button", name="Try it out")
    panel = page.locator(f"#{toggle.get_attribute('aria-controls')}")
    expect(panel).to_have_js_property("inert", True)
    toggle.focus()
    page.keyboard.press("Tab")
    assert not panel.evaluate("el => el.contains(document.activeElement)")

    toggle.click()
    expect(toggle).to_have_attribute("aria-expanded", "true")
    expect(panel).not_to_have_js_property("inert", True)
    panel.get_by_label("status").fill("available")
    panel.get_by_role("button", name="Send request").click()
    expect(panel.locator(".lumina-try-it-status")).to_contain_text("200")
    expect(panel.locator(".lumina-try-it-res-body")).to_contain_text("Luna")

    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert page.locator("dl.http").evaluate_all(
        "els => els.every(el => el.scrollWidth <= el.clientWidth)"
    )
    for control in [copy, toggle, panel.get_by_role("button", name="Send request")]:
        assert control.bounding_box()["height"] >= 44
    toggle.click()
    expect(panel).to_have_js_property("inert", True)
