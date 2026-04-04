# OpenAPI

[sphinxcontrib-openapi](https://sphinxcontrib-openapi.readthedocs.io/) generates HTTP API documentation directly from OpenAPI (Swagger) specification files. It builds on [sphinxcontrib-httpdomain](https://sphinxcontrib-httpdomain.readthedocs.io/), which provides HTTP method directives for writing endpoint docs by hand. Lumina styles all HTTP endpoints with color-coded method indicators.

## Setup

```bash
uv add sphinxcontrib-openapi
```

```python
extensions = ["sphinxcontrib.openapi"]
```

This also installs the HTTP domain, so you can write individual endpoints manually with `http:get::`, `http:post::`, and other method directives.

## Usage

Point the `openapi` directive at your spec file:

```markdown
```{eval-rst}
.. openapi:: path/to/openapi.yml
```
```

See [HTTP API Documentation](../reference/http-api.md) for rendered examples of both auto-generated and manually written HTTP API documentation.
