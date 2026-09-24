"""Exercise the HTTP explorer against mocked APIs; never mutate public demo data."""

import base64
import json
import shlex

import pytest
from playwright.sync_api import expect


@pytest.fixture
def api_page(page, live_server):
    page.add_init_script("""Object.defineProperty(navigator, 'clipboard', {
        value: {writeText: async text => { window.copiedText = text; }}
    });""")
    page.goto(f"{live_server}/reference/http-api.html")
    expect(page.locator(".lumina-try-it")).to_have_count(12)
    return page


def panel(page, signature):
    endpoint = page.locator(f'[id="{signature}"]').locator("..")
    disclosure = endpoint.locator(":scope > dt > .lumina-api-toggle")
    if disclosure.get_attribute("aria-expanded") == "false":
        disclosure.click()
    endpoint.get_by_role("button", name="Try it out").click()
    return endpoint.locator(".lumina-try-it")


def test_required_query_and_response_headers(api_page):
    requests = []

    def respond(route):
        requests.append(route.request)
        route.fulfill(
            status=200,
            content_type="application/json",
            headers={
                "X-Request-ID": "test-123",
                "Access-Control-Expose-Headers": "X-Request-ID",
            },
            body='[{"name":"Milo"}]',
        )

    api_page.route("https://petstore3.swagger.io/**", respond)
    form = panel(api_page, "get--pet-findByStatus")
    form.get_by_role("button", name="Send request").click()
    expect(form.get_by_role("alert").filter(has_text="Enter required")).to_be_visible()
    assert not requests
    form.get_by_label("status").fill("available & pending")
    form.get_by_role("button", name="Send request").click()
    expect(form.locator(".lumina-try-it-status")).to_contain_text("200")
    assert requests[0].url.endswith("?status=available+%26+pending")
    expect(form.get_by_label("Response body")).to_contain_text("Milo")
    form.locator("summary").filter(has_text="Response headers").click()
    expect(form.locator("details").filter(has_text="Response headers")).to_contain_text(
        "x-request-id: test-123"
    )


def test_manual_path_curl_and_empty_response(api_page):
    requests = []
    api_page.route(
        "https://api.example.com/**",
        lambda route: (requests.append(route.request), route.fulfill(status=204)),
    )
    form = panel(api_page, "delete--users-(int-user_id)")
    form.get_by_role("button", name="Send request").click()
    expect(form.get_by_role("alert").filter(has_text="user_id")).to_be_visible()
    form.get_by_label("user_id").fill("a/b ?#")
    form.get_by_role("button", name="Copy as curl").click()
    command = shlex.split(api_page.evaluate("window.copiedText"))
    assert "https://api.example.com/v1/users/a%2Fb%20%3F%23" in command
    form.get_by_role("button", name="Send request").click()
    expect(form.get_by_label("Response body")).to_have_text("(No response body)")
    assert requests[0].method == "DELETE"
    assert requests[0].post_data is None


def test_json_example_validation_curl_and_malformed_response(api_page):
    requests = []
    api_page.route(
        "https://petstore3.swagger.io/**",
        lambda route: (
            requests.append(route.request),
            route.fulfill(
                status=422,
                content_type="application/json",
                body="broken <script>alert(1)</script>",
            ),
        ),
    )
    form = panel(api_page, "post--pet")
    example = json.loads(form.get_by_label("Request body", exact=True).input_value())
    assert example["category"]["name"]
    assert isinstance(example["photoUrls"], list)
    form.get_by_label("Request body", exact=True).fill("{")
    form.get_by_role("button", name="Send request").click()
    expect(form.get_by_role("alert").filter(has_text="not valid JSON")).to_be_visible()
    assert not requests
    body = json.dumps({"name": "O'Reilly $(touch /tmp/not-executed) `id`"})
    form.get_by_label("Request body", exact=True).fill(body)
    form.get_by_role("button", name="Send request").click()
    expect(form.get_by_label("Response body")).to_have_text(
        "broken <script>alert(1)</script>"
    )
    assert form.locator("script").count() == 0
    assert requests[0].post_data == body
    assert requests[0].headers["content-type"] == "application/json"
    # A single copy action uses the edited request.
    expect(api_page.locator(".lumina-curl-copy")).to_have_count(0)
    form.get_by_role("button", name="Copy as curl").click()
    command = shlex.split(api_page.evaluate("window.copiedText"))
    assert command[command.index("--data-raw") + 1] == body


def test_auth_shared_by_server_and_cleared_on_reload(api_page):
    first = panel(api_page, "get--pet-petId")
    first.locator("summary").filter(has_text="Authentication").click()
    first.get_by_label("Type", exact=True).select_option("bearer")
    first.get_by_label("Bearer token", exact=True).fill("test-secret")
    second = panel(api_page, "post--pet-petId")
    second.locator("summary").filter(has_text="Authentication").click()
    expect(second.get_by_label("Bearer token", exact=True)).to_have_value("test-secret")
    second.get_by_label("Server URL").fill("https://other.example/v2")
    second.get_by_label("Server URL").press("Tab")
    expect(second.get_by_label("Type", exact=True)).to_have_value("none")
    expect(first.get_by_label("Bearer token", exact=True)).to_have_value("test-secret")
    first.get_by_role("button", name="Clear credentials", exact=True).click()
    expect(first.get_by_label("Type", exact=True)).to_have_value("none")
    first.get_by_label("Type", exact=True).select_option("bearer")
    first.get_by_label("Bearer token", exact=True).fill("another-secret")
    api_page.reload()
    first = panel(api_page, "get--pet-petId")
    first.locator("summary").filter(has_text="Authentication").click()
    expect(first.get_by_label("Type", exact=True)).to_have_value("none")


@pytest.mark.parametrize("mode", ["basic", "header", "query"])
def test_authentication_sent_as_configured(api_page, mode):
    requests = []
    api_page.route(
        "https://petstore3.swagger.io/**",
        lambda route: (
            requests.append(route.request),
            route.fulfill(status=200, body="ok"),
        ),
    )
    form = panel(api_page, "get--store-inventory")
    form.locator("summary").filter(has_text="Authentication").click()
    form.get_by_label("Type", exact=True).select_option(
        "basic" if mode == "basic" else "apiKey"
    )
    if mode == "basic":
        form.get_by_label("Username", exact=True).fill("reader")
        form.get_by_label("Password", exact=True).fill("p@ss")
    else:
        form.get_by_label("Key name", exact=True).fill("X-API-Key")
        form.get_by_label("Key value", exact=True).fill("test&key")
        form.get_by_label("Send in", exact=True).select_option(mode)
    form.get_by_role("button", name="Send request").click()
    expect(form.get_by_label("Response body")).to_have_text("ok")
    if mode == "basic":
        assert (
            requests[0].headers["authorization"]
            == "Basic " + base64.b64encode(b"reader:p@ss").decode()
        )
    elif mode == "header":
        assert requests[0].headers["x-api-key"] == "test&key"
    else:
        assert requests[0].url.endswith("?X-API-Key=test%26key")


def test_cancel_and_timeout(api_page):
    api_page.evaluate("""() => { window.fetch = (url, options) => new Promise((resolve, reject) => {
        options.signal.addEventListener('abort', () => reject(options.signal.reason));
    }); }""")
    form = panel(api_page, "get--store-inventory")
    form.get_by_role("button", name="Send request").click()
    form.get_by_role("button", name="Cancel", exact=True).click()
    expect(form.locator(".lumina-try-it-status")).to_have_text("Cancelled")
    expect(form.get_by_role("button", name="Send request")).to_be_enabled()
    api_page.clock.install()
    form.get_by_role("button", name="Send request").click()
    api_page.clock.fast_forward(31000)
    expect(form.get_by_label("Response body")).to_contain_text("timed out")
    expect(form.get_by_role("button", name="Send request")).to_be_enabled()


def test_accessible_panels_and_mobile_layout(api_page):
    assert api_page.locator(".lumina-try-it-grid[inert]").count() == 12
    forms = [panel(api_page, "get--pet-petId"), panel(api_page, "post--pet-petId")]
    ids = api_page.locator(".lumina-try-it [id]").evaluate_all(
        "els => els.map(el => el.id)"
    )
    assert len(ids) == len(set(ids))
    for form in forms:
        form.get_by_label("petId").fill("42")
        expect(form.get_by_label("petId")).to_have_value("42")
    api_page.set_viewport_size({"width": 390, "height": 844})
    for theme in ["light", "dark"]:
        api_page.evaluate(
            "theme => document.documentElement.dataset.theme = theme", theme
        )
        assert api_page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert forms[0].locator(".lumina-try-it-grid").get_attribute("inert") is None


def test_raw_body_custom_headers_and_keyboard_send(api_page):
    requests = []

    def respond(route):
        requests.append(route.request)
        route.fulfill(status=200, content_type="text/plain", body="accepted")

    api_page.route("https://api.example.com/**", respond)
    form = panel(api_page, "post--users")
    form.get_by_label("Content type", exact=True).fill("text/plain")
    form.get_by_label("Request body", exact=True).fill("raw body, not JSON")
    form.locator("summary").filter(has_text="Additional headers").click()
    form.get_by_role("button", name="Add header").click()
    form.get_by_label("Header name", exact=True).fill("Invalid header")
    form.get_by_label("Header value", exact=True).fill("test-value")
    form.get_by_role("button", name="Send request").click()
    expect(form.get_by_role("alert").filter(has_text="header")).to_be_visible()
    assert not requests
    form.get_by_label("Header name", exact=True).fill("X-Test")
    form.get_by_label("Request body", exact=True).press("Control+Enter")
    expect(form.get_by_label("Response body")).to_have_text("accepted")
    assert requests[0].post_data == "raw body, not JSON"
    assert requests[0].headers["content-type"] == "text/plain"
    assert requests[0].headers["x-test"] == "test-value"


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
