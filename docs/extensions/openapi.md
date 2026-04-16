# OpenAPI

[sphinxcontrib-openapi](https://sphinxcontrib-openapi.readthedocs.io/) generates HTTP API documentation directly from OpenAPI (Swagger) specification files. It builds on [sphinxcontrib-httpdomain](https://sphinxcontrib-httpdomain.readthedocs.io/), which provides HTTP method directives for writing endpoint docs by hand. Lumina styles all HTTP endpoints with color-coded method indicators and adds interactive features when you configure a base URL.

## Setup

```bash
uv add sphinxcontrib-openapi
```

```{code-block} python
:caption: conf.py
extensions = ["sphinxcontrib.openapi"]
```

This also installs the HTTP domain, so you can write individual endpoints manually with `http:get::`, `http:post::`, and other method directives.

## Usage

Point the `openapi` directive at your spec file:

````markdown
```{eval-rst}
.. openapi:: path/to/openapi.yml
```
````

See {doc}`/reference/http-api` for rendered examples of both auto-generated and manually written HTTP API documentation.

## Interactive Features

Set `api_base_url` in your theme options to activate two interactive features on every HTTP endpoint:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "api_base_url": "https://api.example.com/v1",
}
```

### Copy as curl

A **Copy as curl** button appears in the signature bar of each endpoint. Clicking it copies a ready-to-run `curl` command to your clipboard, with:

- The correct HTTP method and full URL (base URL + path)
- All documented request headers (e.g., `Authorization: Bearer <token>`)
- A JSON body template pre-populated from documented request fields
- Query parameters shown as `?param=<value>` placeholders

For endpoints with multiple flags the command uses multi-line formatting for readability:

```bash
curl -X POST "https://api.example.com/v1/users" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"email":"","name":"","role":""}'
```

### Try it out

A collapsible **Try it out** panel sits below each endpoint description. It lets readers send real HTTP requests directly from the docs page without leaving the browser.

The panel pre-populates from the documented endpoint:

- **Path parameters** — required fields with live URL preview as you type
- **Query parameters** — optional fields shown with their types
- **Authorization** — bearer token input (hidden by default; persisted in `sessionStorage` across page loads)
- **Additional headers** — any other documented request headers
- **Request body** — JSON textarea pre-filled with a schema template for POST/PUT/PATCH endpoints

After sending, the panel shows the HTTP status code, response time in milliseconds, and a syntax-highlighted JSON response body (or plain text for non-JSON responses).

:::{warning}
**CORS required.** The "Try it out" panel sends requests directly from the reader's browser. Your API must allow CORS from the docs origin, or requests fail with a network error. Many public APIs (Stripe, GitHub, Petstore) already support this.
:::

### Overriding the base URL per block

`api_base_url` sets a global default for all endpoints on all pages. To use a different server URL for a specific group of endpoints — for example, a staging environment or a separate microservice — wrap those endpoints in a `<div>` with a `data-api-base-url` attribute.

The closest ancestor's `data-api-base-url` takes precedence over the global setting:

````{code-block} markdown
<div data-api-base-url="https://staging.api.example.com/v1">

```{eval-rst}
.. openapi:: staging-api.yml
```

</div>
````

This works with both `.. openapi::` directives and individual `.. http:get::` / `.. http:post::` directives.

:::{note}
HTML blocks in MyST require `html_block` in `myst_enable_extensions`, or use a `{raw} html` directive pair instead:

````markdown
```{raw} html
<div data-api-base-url="https://staging.api.example.com/v1">
```

```{eval-rst}
.. openapi:: staging-api.yml
```

```{raw} html
</div>
```
````
:::

The server badge (shown above the first endpoint) always reflects the global `api_base_url`. Per-block overrides affect only the curl commands and "Try it out" URLs.

### Disabling Try it out

To keep the "Copy as curl" button but hide the interactive panel:

```{code-block} python
:caption: conf.py
html_theme_options = {
    "api_base_url": "https://api.example.com/v1",
    "try_it_out": "false",
}
```

### Bearer token persistence

When a reader enters a bearer token in the "Try it out" panel, it is saved to `sessionStorage` under the key `lumina-api-token`. The token is restored automatically when the panel is opened on any endpoint in the same browser tab. It is never sent to any server other than your API.

The token is cleared when the browser tab is closed (sessionStorage scope).
