# OpenAPI

[sphinxcontrib-openapi](https://sphinxcontrib-openapi.readthedocs.io/) generates HTTP API documentation directly from OpenAPI (Swagger) specification files. It builds on [sphinxcontrib-httpdomain](https://sphinxcontrib-httpdomain.readthedocs.io/), which provides HTTP method directives for writing endpoint docs by hand. Lumina styles all HTTP endpoints with color-coded method indicators and adds interactive features when you configure a base URL.

## Setup

```bash
uv add sphinxcontrib-openapi
```

```python
extensions = ["sphinxcontrib.openapi"]
openapi_default_renderer = "httpdomain"
```

Use the `httpdomain` renderer for OpenAPI 3 request schemas and examples. The extension’s legacy default renderer can omit request bodies.

This also installs the HTTP domain, so you can write individual endpoints manually with `http:get::`, `http:post::`, and other method directives.

## Usage

Point the `openapi` directive at your spec file:

```markdown
```{eval-rst}
.. openapi:: path/to/openapi.yml
   :generate-examples-from-schemas:
```
```

See [HTTP API Documentation](../reference/http-api.md) for rendered examples of both auto-generated and manually written HTTP API documentation.

## Interactive Features

Set `api_base_url` in your theme options to activate two interactive features on every HTTP endpoint:

```python
html_theme_options = {
    "api_base_url": "https://api.example.com/v1",
}
```

### Copy as curl

A **Copy as curl** button appears in each endpoint’s signature and request panel. With **Try it out** enabled, both buttons copy the current server, parameters, headers, authentication, and body. Open **Request command** to inspect or manually copy the command.

Commands use POSIX shell quoting, including apostrophes in JSON and headers. Fill in required parameters before running them. Treat copied commands as sensitive when they include credentials.

When **Try it out** is disabled, the signature button copies a template from the documented fields and request example. Replace parameter placeholders before running it.

### Try it out

Open an endpoint’s **Try it out** panel:

1. Check **Server URL**. You can change it for this endpoint without rebuilding the docs.
2. Fill in path parameters and any query parameters marked required.
3. Open **Authentication** if needed, then edit headers or the request body.
4. Choose **Send Request** or **Copy as curl**. You can also send with **Ctrl+Enter** (macOS: **⌘+Enter**) from a request field.

The editor supports:

- **Path parameters** in OpenAPI `{id}` and HTTP-domain `(int:id)` notation, with URL encoding.
- **Query parameters** and required markers from rendered documentation.
- **Authentication** using Bearer tokens, Basic authentication, or API keys in headers or query strings.
- **Headers**, including documented defaults written as inline code, and additional name/value pairs.
- **Request bodies** populated from rendered HTTP request examples. Use `:generate-examples-from-schemas:` to generate nested JSON examples from your specification.

Without an example, documented top-level JSON fields provide a basic template. Check it against your API’s schema. A blank editor sends no body. JSON is checked for valid syntax before sending; it is not validated against the OpenAPI schema. You can change **Content type** to send raw text, XML, or a manually encoded form body.

Responses show the HTTP status, elapsed time through body download, response URL, exposed headers, and body. JSON is formatted and highlighted. Malformed JSON and non-JSON responses remain visible as text.

**Cancel** stops waiting for a response; the server may still process the request. Requests time out after 30 seconds. **Clear** removes the response while retaining your inputs.

#### WARNING
**CORS required.** Requests go directly from the reader’s browser to the API. Allow the docs origin, request methods, and headers in your API’s CORS configuration. Expose diagnostic response headers such as `X-Request-ID` with `Access-Control-Expose-Headers`.

Browser cookies are omitted, browser-controlled headers cannot be overridden, and redirects are rejected to avoid forwarding credentials to another destination. Use the final API URL. If a request fails, check HTTPS, connectivity, and CORS, or use **Copy as curl** outside the browser.

### Authentication and credential lifetime

Choose the authentication type explicitly. Lumina does not infer OpenAPI `securitySchemes` or run OAuth login flows.

Authentication settings are shared between endpoints with the same full API base URL on the current page. Changing **Server URL** selects that server’s separate credentials. **Clear credentials** clears authentication for all endpoints using that server.

Credentials stay in page memory only. Reloading or navigating away clears them; they are not saved in browser storage. Use narrowly scoped test credentials on trusted documentation hosts. API keys sent in query strings also appear in the URL preview and may be recorded in server logs.

### When this can replace Swagger UI

Lumina suits documentation sites that need readable endpoint references and interactive testing of ordinary JSON or raw-body REST requests, including Bearer, Basic, and API-key authentication.

It is not a complete OpenAPI execution engine. The editor reads rendered HTTP-domain documentation, so it cannot recover specification details the renderer omits. Use a dedicated OpenAPI client when you need:

- Automatic server variables, security requirements, or OAuth2/OpenID Connect login flows.
- Schema-aware validation, enum selectors, or selectable `oneOf`/`anyOf` variants.
- OpenAPI array/object parameter serialization (`style`, `explode`, `deepObject`), repeated query keys, or cookie authentication.
- Multipart file uploads, binary response downloads, or streaming responses.

For these cases, keep the specification available to download alongside your Lumina reference. Do not assume that a rendered schema implies full interactive support.

### Overriding the base URL per block

`api_base_url` sets a global default for all endpoints on all pages. To use a different server URL for a specific group of endpoints — for example, a staging environment or a separate microservice — wrap those endpoints in a `<div>` with a `data-api-base-url` attribute.

The closest ancestor’s `data-api-base-url` takes precedence over the global setting:

```markdown
<div data-api-base-url="https://staging.api.example.com/v1">

```{eval-rst}
.. openapi:: staging-api.yml
```

</div>
```

This works with both `.. openapi::` directives and individual `.. http:get::` / `.. http:post::` directives.

#### NOTE
HTML blocks in MyST require `html_block` in `myst_enable_extensions`, or use a `{raw} html` directive pair instead:

```markdown
```{raw} html
<div data-api-base-url="https://staging.api.example.com/v1">
```

```{eval-rst}
.. openapi:: staging-api.yml
```

```{raw} html
</div>
```
```

Each signature shows its configured server hostname. The **Server URL** field and live request preview show the destination used by the request editor, including reader edits.

### Disabling Try it out

To keep the “Copy as curl” button but hide the interactive panel:

```python
html_theme_options = {
    "api_base_url": "https://api.example.com/v1",
    "try_it_out": "false",
}
```
