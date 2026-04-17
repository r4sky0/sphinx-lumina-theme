# HTTP API Documentation

How HTTP API endpoints render in the Lumina theme. This page covers auto-generated docs from OpenAPI specs and manually written HTTP directives.

:::{tip}
See {doc}`/extensions/openapi` for installation, setup, and interactive feature documentation (copy as curl and Try it out).
:::

## From an OpenAPI Spec

The `openapi` directive renders an entire API from a spec file. Point it at your OpenAPI (Swagger) YAML or JSON:

```{eval-rst}
.. openapi:: openapi-petstore.yml
```

The MyST syntax:

~~~markdown
```{eval-rst}
.. openapi:: openapi-petstore.yml
```
~~~

## Manual HTTP Directives

For individual endpoints or when you need more control, use the HTTP domain directives directly.

### GET Request

```{eval-rst}
.. http:get:: /users

   Returns a paginated list of users.

   :query page: Page number (default ``1``).
   :query per_page: Results per page (default ``20``, max ``100``).
   :reqheader Authorization: Bearer token.
   :reqheader Accept: ``application/json``
   :status 200: A JSON array of user objects.
   :status 401: Authentication required.
```

### POST Request

```{eval-rst}
.. http:post:: /users

   Creates a new user account.

   :<json string email: The user's email address (required).
   :<json string name: Display name (required).
   :<json string role: One of ``admin``, ``editor``, or ``viewer`` (default ``viewer``).
   :reqheader Authorization: Bearer token with admin scope.
   :reqheader Content-Type: ``application/json``
   :status 201: The newly created user object.
   :status 409: A user with this email already exists.
   :status 422: Validation failed.
```

### DELETE Request

```{eval-rst}
.. http:delete:: /users/(int:user_id)

   Permanently deletes a user account. This action cannot be undone.

   :param user_id: The unique user identifier.
   :reqheader Authorization: Bearer token with admin scope.
   :status 204: User deleted successfully.
   :status 404: User not found.
```

### Per-block URL Override

When some endpoints live on a different server than the global `api_base_url`, wrap their directives in a `<div data-api-base-url="...">`. The "Try it out" panel and curl commands for those endpoints will use the override URL.

```{raw} html
<div data-api-base-url="https://reports.api.example.com/v2">
```

```{eval-rst}
.. http:get:: /reports

   Returns available reports for the current user.

   :reqheader Authorization: Bearer token.
   :status 200: A list of report objects.
   :status 401: Authentication required.

.. http:post:: /reports

   Queues a new report for generation.

   :<json string type: Report type: ``summary``, ``detail``, or ``audit``.
   :<json string from: Start date in ``YYYY-MM-DD`` format.
   :<json string to: End date in ``YYYY-MM-DD`` format.
   :reqheader Authorization: Bearer token.
   :reqheader Content-Type: ``application/json``
   :status 202: Report generation queued.
   :status 422: Validation failed.
```

```{raw} html
</div>
```

The "Try it out" buttons above use `https://reports.api.example.com/v2` while the GET and POST `/users` endpoints above them use the global URL. The MyST syntax:

~~~markdown
```{raw} html
<div data-api-base-url="https://other.api.example.com/v2">
```

```{eval-rst}
.. http:get:: /endpoint
   ...
```

```{raw} html
</div>
```
~~~

The MyST syntax for manual directives:

~~~markdown
```{eval-rst}
.. http:get:: /endpoint

   Description of the endpoint.

   :query param_name: Parameter description.
   :status 200: Success response description.
```
~~~

## Cross-Referencing

Reference documented HTTP endpoints from anywhere using the `:http:get:`, `:http:post:`, and other method roles.

```{eval-rst}
Use :http:get:`/users` to list users, :http:post:`/users` to create one, or :http:delete:`/users/(int:user_id)` to remove an account.
```

The syntax:

```markdown
:http:get:`/users`
:http:post:`/users`
:http:delete:`/users/(int:user_id)`
```
