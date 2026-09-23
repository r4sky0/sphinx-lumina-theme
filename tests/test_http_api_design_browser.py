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
    expect(endpoint.locator(".lumina-curl-copy")).to_have_count(0)

    endpoint.locator(".lumina-api-toggle").click()
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
    copy = panel.locator(".lumina-try-it-actions button").filter(
        has_text="Copy as curl"
    )
    expect(copy).to_have_count(1)
    copy.click()
    expect(panel.get_by_role("button", name="Copied!", exact=True)).to_be_visible()
    assert "status=available" in page.evaluate("window.copiedCurl")
    panel.get_by_role("button", name="Send request").click()
    expect(panel.locator(".lumina-try-it-status")).to_contain_text("200")
    expect(panel.get_by_label("Response body")).to_contain_text("Luna")

    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert page.locator("dl.http").evaluate_all(
        "els => els.every(el => el.scrollWidth <= el.clientWidth)"
    )
    for control in [toggle, panel.get_by_role("button", name="Send request")]:
        assert round(control.bounding_box()["height"], 2) >= 44
    toggle.click()
    expect(panel).to_have_js_property("inert", True)


@pytest.mark.parametrize(
    "path,domain", [("http-api", "http"), ("api-documentation", "py")]
)
@pytest.mark.parametrize("width", [390, 1440])
def test_api_disclosures(page, live_server, path, domain, width):
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(f"{live_server}/reference/{path}.html")
    definitions = page.locator(f"dl.{domain}")
    bodies = definitions.locator(":scope > dd")
    expect(bodies.first).to_be_hidden()
    disclosure = definitions.first.locator(":scope > dt > .lumina-api-toggle")
    disclosure.focus()
    page.keyboard.press("Enter")
    expect(bodies.first).to_be_visible()
    expect(disclosure).to_have_attribute("aria-expanded", "true")
    for theme in ["light", "dark"]:
        page.evaluate("theme => document.documentElement.dataset.theme = theme", theme)
        page.get_by_role("button", name="Expand all", exact=True).click()
        assert bodies.evaluate_all("els => els.every(el => !el.hidden)")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.get_by_role("button", name="Collapse all", exact=True).click()
        assert bodies.evaluate_all("els => els.every(el => el.hidden)")
    signature_id = definitions.first.locator(":scope > dt").get_attribute("id")
    page.goto(f"{live_server}/reference/{path}.html#{signature_id}")
    expect(bodies.first).to_be_visible()
    expect(bodies.nth(1)).to_be_hidden()


def test_api_expanded_default_and_nested_links(page, live_server):
    def expanded_page(route):
        response = route.fetch()
        route.fulfill(
            response=response,
            body=response.text().replace(
                "</head>",
                '<script>document.documentElement.dataset.apiExpanded = "true";</script></head>',
            ),
        )

    page.route("**/reference/api-documentation.html", expanded_page)
    page.goto(f"{live_server}/reference/api-documentation.html")
    expect(page.locator(".lumina-api-toggle").first).to_have_attribute(
        "aria-expanded", "true"
    )
    assert page.locator("dl.py > dd").evaluate_all("els => els.every(el => !el.hidden)")
    page.get_by_role("button", name="Collapse all", exact=True).click()
    # Autodoc can nest methods inside class bodies. A member link must open both.
    page.evaluate("""() => {
        const parent = document.querySelector('dl.py.class > dd');
        const method = document.querySelector('dl.py.method');
        parent.appendChild(method);
        location.hash = method.querySelector('dt').id;
    }""")
    expect(page.locator("dl.py.class > dd")).to_be_visible()
    expect(page.locator("dl.py.class dl.py.method > dd")).to_be_visible()


def test_single_curl_fallback_without_request_panels(page, live_server):
    page.add_init_script(
        "navigator.clipboard.writeText = async text => { window.copiedCurl = text; };"
    )

    def disable_panels(route):
        response = route.fetch()
        route.fulfill(
            response=response,
            body=response.text().replace(
                "</head>",
                '<script>document.documentElement.dataset.tryItOut = "false";</script></head>',
            ),
        )

    page.route("**/reference/http-api.html", disable_panels)
    page.goto(f"{live_server}/reference/http-api.html")
    expect(page.locator(".lumina-try-it")).to_have_count(0)
    endpoint = page.locator("dl.http").first
    copy = endpoint.locator(".lumina-curl-copy")
    expect(copy).to_have_count(1)
    copy.click()
    expect(copy).to_have_text("Copied!")
    assert "/pet/findByStatus" in page.evaluate("window.copiedCurl")
    expect(endpoint.locator(":scope > dd")).to_be_hidden()
