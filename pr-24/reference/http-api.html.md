# HTTP API Documentation

How HTTP API endpoints render in the Lumina theme. This page covers auto-generated docs from OpenAPI specs and manually written HTTP directives.

## From an OpenAPI Spec

The `openapi` directive renders an entire API from a spec file. Point it at your OpenAPI (Swagger) YAML or JSON:

### GET /tasks

**List tasks**

Returns all tasks, optionally filtered by status.

* **Query Parameters:**
  * **status** (*string*) – Filter by task status.
* **Status Codes:**
  * [200 OK](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/200) – An array of tasks.

### POST /tasks

**Create a task**

Creates a new task and returns it.

* **Status Codes:**
  * [201 Created](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/201) – The newly created task.

### GET /tasks/{task_id}

**Get a task**

Returns a single task by its ID.

* **Parameters:**
  * **task_id** (*integer*) – Unique task identifier.
* **Status Codes:**
  * [200 OK](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/200) – The requested task.
  * [404 Not Found](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/404) – Task not found.

### PATCH /tasks/{task_id}

**Update a task**

Updates an existing task. Only provided fields are changed.

* **Parameters:**
  * **task_id** (*integer*) – Unique task identifier.
* **Status Codes:**
  * [200 OK](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/200) – The updated task.
  * [404 Not Found](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/404) – Task not found.

### DELETE /tasks/{task_id}

**Delete a task**

Permanently removes a task.

* **Parameters:**
  * **task_id** (*integer*) – Unique task identifier.
* **Status Codes:**
  * [204 No Content](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/204) – Task deleted successfully.
  * [404 Not Found](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/404) – Task not found.

The MyST syntax:

```markdown
```{eval-rst}
.. openapi:: openapi-tasks.yml
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
