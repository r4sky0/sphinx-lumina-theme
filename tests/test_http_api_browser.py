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
    # The signature button must copy the same edited request as the panel button.
    form.locator("..").locator("..").locator(".lumina-curl-copy").click()
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
