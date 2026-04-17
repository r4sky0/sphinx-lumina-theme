# HTTP API Documentation

How HTTP API endpoints render in the Lumina theme. This page covers auto-generated docs from OpenAPI specs and manually written HTTP directives.

## From an OpenAPI Spec

The `openapi` directive renders an entire API from a spec file. Point it at your OpenAPI (Swagger) YAML or JSON:

### GET /pet/findByStatus

**Finds Pets by status.**

Multiple status values can be provided with comma separated strings.

* **Query Parameters:**
  * **status** (*string*) – Status values that need to be considered for filter
    (Required)
* **Status Codes:**
  * [200 OK](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/200) – successful operation
  * [400 Bad Request](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/400) – Invalid status value

### GET /pet/{petId}

**Find pet by ID.**

Returns a single pet.

* **Parameters:**
  * **petId** (*integer*) – ID of pet to return
* **Status Codes:**
  * [200 OK](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/200) – successful operation
  * [400 Bad Request](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/400) – Invalid ID supplied
  * [404 Not Found](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/404) – Pet not found

### POST /pet/{petId}

**Updates a pet in the store with form data.**

Updates a pet resource based on the form data.

* **Parameters:**
  * **petId** (*integer*) – ID of pet that needs to be updated
* **Query Parameters:**
  * **name** (*string*) – Name of pet that needs to be updated
  * **status** (*string*) – Status of pet that needs to be updated
* **Status Codes:**
  * [200 OK](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/200) – successful operation
  * [400 Bad Request](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/400) – Invalid input

### DELETE /pet/{petId}

**Deletes a pet.**

Delete a pet.

* **Parameters:**
  * **petId** (*integer*) – Pet id to delete
* **Status Codes:**
  * [200 OK](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/200) – Pet deleted
  * [400 Bad Request](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/400) – Invalid pet value
* **Request Headers:**
  * **api_key**

### POST /pet

**Add a new pet to the store.**

Add a new pet to the store.

* **Status Codes:**
  * [200 OK](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/200) – Successful operation
  * [400 Bad Request](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/400) – Invalid input
  * [422 Unprocessable Entity](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/422) – Validation exception

### GET /store/inventory

**Returns pet inventories by status.**

Returns a map of status codes to quantities.

* **Status Codes:**
  * [200 OK](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/200) – successful operation

### POST /store/order

**Place an order for a pet.**

Place a new order in the store.

* **Status Codes:**
  * [200 OK](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/200) – successful operation
  * [400 Bad Request](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/400) – Invalid input
  * [422 Unprocessable Entity](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/422) – Validation exception

The MyST syntax:

```markdown
```{eval-rst}
.. openapi:: openapi-petstore.yml
```
```

## Manual HTTP Directives

For individual endpoints or when you need more control, use the HTTP domain directives directly.

### GET Request

### GET /users

Returns a paginated list of users.

* **Query Parameters:**
  * **page** – Page number (default `1`).
  * **per_page** – Results per page (default `20`, max `100`).
* **Request Headers:**
  * **Authorization** – Bearer token.
  * **Accept** – `application/json`
* **Status Codes:**
  * [200 OK](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/200) – A JSON array of user objects.
  * [401 Unauthorized](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/401) – Authentication required.

### POST Request

### POST /users

Creates a new user account.

* **Request JSON Object:**
  * **email** (*string*) – The user’s email address (required).
  * **name** (*string*) – Display name (required).
  * **role** (*string*) – One of `admin`, `editor`, or `viewer` (default `viewer`).
* **Request Headers:**
  * **Authorization** – Bearer token with admin scope.
  * **Content-Type** – `application/json`
* **Status Codes:**
  * [201 Created](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/201) – The newly created user object.
  * [409 Conflict](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/409) – A user with this email already exists.
  * [422 Unprocessable Entity](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/422) – Validation failed.

### DELETE Request

### DELETE /users/(*int:* user_id)

Permanently deletes a user account. This action cannot be undone.

* **Parameters:**
  * **user_id** – The unique user identifier.
* **Request Headers:**
  * **Authorization** – Bearer token with admin scope.
* **Status Codes:**
  * [204 No Content](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/204) – User deleted successfully.
  * [404 Not Found](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/404) – User not found.

### Per-block URL Override

When some endpoints live on a different server than the global `api_base_url`, wrap their directives in a `<div data-api-base-url="...">`. The “Try it out” panel and curl commands for those endpoints will use the override URL.

<div data-api-base-url="https://reports.api.example.com/v2">

### GET /reports

Returns available reports for the current user.

* **Request Headers:**
  * **Authorization** – Bearer token.
* **Status Codes:**
  * [200 OK](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/200) – A list of report objects.
  * [401 Unauthorized](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/401) – Authentication required.

### POST /reports

Queues a new report for generation.

* **Request JSON Object:**
  * **type** (*string*) – Report type: `summary`, `detail`, or `audit`.
  * **from** (*string*) – Start date in `YYYY-MM-DD` format.
  * **to** (*string*) – End date in `YYYY-MM-DD` format.
* **Request Headers:**
  * **Authorization** – Bearer token.
  * **Content-Type** – `application/json`
* **Status Codes:**
  * [202 Accepted](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/202) – Report generation queued.
  * [422 Unprocessable Entity](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/422) – Validation failed.

</div>

The “Try it out” buttons above use `https://reports.api.example.com/v2` while the GET and POST `/users` endpoints above them use the global URL. The MyST syntax:

```markdown
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
```

The MyST syntax for manual directives:

```markdown
```{eval-rst}
.. http:get:: /endpoint

   Description of the endpoint.

   :query param_name: Parameter description.
   :status 200: Success response description.
```
```

## Cross-Referencing

Reference documented HTTP endpoints from anywhere using the `:http:get:`, `:http:post:`, and other method roles.

Use [`GET /users`](#get--users) to list users, [`POST /users`](#post--users) to create one, or [`DELETE /users/(int:user_id)`](#delete--users-(int-user_id)) to remove an account.

The syntax:

```markdown
:http:get:`/users`
:http:post:`/users`
:http:delete:`/users/(int:user_id)`
```
