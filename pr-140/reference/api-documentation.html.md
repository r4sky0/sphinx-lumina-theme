# API Documentation

How technical API documentation renders in the Lumina theme. This page covers manually written API docs and autodoc integration.

## Functions

### connect(host: str, port: int, , timeout: float = 30.0) → Connection

Connect to a remote server.

* **Parameters:**
  * **host** – The hostname or IP address.
  * **port** – The port number (1–65535).
  * **timeout** – Connection timeout in seconds.
* **Returns:**
  An active connection object.
* **Raises:**
  * **ConnectionError** – If the server is unreachable.
  * **ValueError** – If the port is out of range.

The MyST syntax:

```markdown
```{py:function} connect(host: str, port: int) -> Connection
Description of the function.

:param host: Parameter description.
:returns: Return value description.
:raises ConnectionError: When this error occurs.
```
```

## Classes

### *class* EventEmitter

A simple event emitter that supports registering handlers and emitting events.

#### EventEmitter.on(event: str, handler: Callable) → None

Register a handler for the given event name.

* **Parameters:**
  * **event** – The event name to listen for.
  * **handler** – A callable invoked when the event is emitted.

#### EventEmitter.emit(event: str, \*args, \*\*kwargs) → None

Emit an event, calling all registered handlers.

* **Parameters:**
  * **event** – The event name to emit.
  * **args** – Positional arguments passed to handlers.
  * **kwargs** – Keyword arguments passed to handlers.

#### EventEmitter.off(event: str, handler: Callable) → None

Remove a previously registered handler.

* **Parameters:**
  * **event** – The event name.
  * **handler** – The handler to remove.
* **Raises:**
  **ValueError** – If the handler is not registered for this event.

#### EventEmitter.handlers *: dict[str, list[Callable]]*

A mapping of event names to their registered handler lists.

The MyST syntax for classes:

```markdown
```{py:class} ClassName()
Class description.
```

```{py:method} ClassName.method_name(param: type) -> return_type
Method description.

:param param: Parameter description.
```
```

## Cross-Referencing API Items

Reference documented API items from anywhere using the `{py:func}`, `{py:class}`, and `{py:meth}` roles.

Use [`connect()`](#connect) to establish a connection, then create an [`EventEmitter`](#EventEmitter) instance and call [`EventEmitter.on()`](#EventEmitter.on) to register handlers.

The MyST syntax:

```markdown
{py:func}`connect`
{py:class}`EventEmitter`
{py:meth}`EventEmitter.on`
```

## Deprecation Notices

Mark API items as deprecated directly in their documentation.

### legacy_connect(host: str) → Connection

.. deprecated::
Use [`connect()`](#connect) instead, which supports timeout and port configuration.

## Module-Level Documentation

The main module for the Sphinx Lumina Theme.

### sphinx_lumina_theme.DEFAULT_ACCENT_COLOR *: str* *= #10b981*

The default accent color used when no custom `accent_color` is configured.

### sphinx_lumina_theme.SUPPORTED_SEARCH_BACKENDS *: tuple[str, ...]* *= ("pagefind", "sphinx")*

Tuple of supported search backend identifiers.

## Using autodoc

For real projects, you’ll typically generate API docs from your source code using `sphinx.ext.autodoc` instead of writing signatures by hand.

### Setup

```python
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",     # Google/NumPy docstring support
    "sphinx.ext.viewcode",     # Link to highlighted source
]
```

### Documenting a Module

Create a `.md` or `.rst` file and use the `automodule`, `autoclass`, or `autofunction` directives:

```markdown
## API Reference

```{automodule} mypackage.core
:members:
:undoc-members:
:show-inheritance:
```
```

### Documenting Individual Items

```markdown
```{autofunction} mypackage.connect
```

```{autoclass} mypackage.EventEmitter
:members:
:special-members: __init__
```
```

### autodoc Options

| Option                | Description                                                     |
|-----------------------|-----------------------------------------------------------------|
| `:members:`           | Include all public members.                                     |
| `:undoc-members:`     | Include members without docstrings.                             |
| `:private-members:`   | Include `_private` members.                                     |
| `:special-members:`   | Include `__dunder__` methods (specify which, e.g., `__init__`). |
| `:show-inheritance:`  | Show base classes.                                              |
| `:inherited-members:` | Include members inherited from base classes.                    |
| `:exclude-members:`   | Comma-separated list of members to skip.                        |
