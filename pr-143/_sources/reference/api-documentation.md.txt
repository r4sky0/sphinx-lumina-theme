# API Documentation

How technical API documentation renders in the Lumina theme. This page covers manually written API docs and autodoc integration.

## Functions

```{py:function} connect(host: str, port: int, *, timeout: float = 30.0) -> Connection
Connect to a remote server.

:param host: The hostname or IP address.
:param port: The port number (1–65535).
:param timeout: Connection timeout in seconds.
:returns: An active connection object.
:raises ConnectionError: If the server is unreachable.
:raises ValueError: If the port is out of range.
```

The MyST syntax:

~~~markdown
```{py:function} connect(host: str, port: int) -> Connection
Description of the function.

:param host: Parameter description.
:returns: Return value description.
:raises ConnectionError: When this error occurs.
```
~~~

## Classes

```{py:class} EventEmitter()
A simple event emitter that supports registering handlers and emitting events.
```

```{py:method} EventEmitter.on(event: str, handler: Callable) -> None
Register a handler for the given event name.

:param event: The event name to listen for.
:param handler: A callable invoked when the event is emitted.
```

```{py:method} EventEmitter.emit(event: str, *args, **kwargs) -> None
Emit an event, calling all registered handlers.

:param event: The event name to emit.
:param args: Positional arguments passed to handlers.
:param kwargs: Keyword arguments passed to handlers.
```

```{py:method} EventEmitter.off(event: str, handler: Callable) -> None
Remove a previously registered handler.

:param event: The event name.
:param handler: The handler to remove.
:raises ValueError: If the handler is not registered for this event.
```

```{py:attribute} EventEmitter.handlers
:type: dict[str, list[Callable]]

A mapping of event names to their registered handler lists.
```

The MyST syntax for classes:

~~~markdown
```{py:class} ClassName()
Class description.
```

```{py:method} ClassName.method_name(param: type) -> return_type
Method description.

:param param: Parameter description.
```
~~~

## Cross-Referencing API Items

Reference documented API items from anywhere using the `{py:func}`, `{py:class}`, and `{py:meth}` roles.

Use {py:func}`connect` to establish a connection, then create an {py:class}`EventEmitter` instance and call {py:meth}`EventEmitter.on` to register handlers.

The MyST syntax:

```markdown
{py:func}`connect`
{py:class}`EventEmitter`
{py:meth}`EventEmitter.on`
```

## Deprecation Notices

Mark API items as deprecated directly in their documentation.

```{py:function} legacy_connect(host: str) -> Connection

.. deprecated::
   Use {py:func}`connect` instead, which supports timeout and port configuration.
```

## Module-Level Documentation

```{py:module} sphinx_lumina_theme
The main module for the Sphinx Lumina Theme.
```

```{py:data} DEFAULT_ACCENT_COLOR
:type: str
:value: "#10b981"

The default accent color used when no custom `accent_color` is configured.
```

```{py:data} SUPPORTED_SEARCH_BACKENDS
:type: tuple[str, ...]
:value: ("pagefind", "sphinx")

Tuple of supported search backend identifiers.
```

## Using autodoc

For real projects, you'll typically generate API docs from your source code using `sphinx.ext.autodoc` instead of writing signatures by hand.

### Setup

```{code-block} python
:caption: conf.py
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",     # Google/NumPy docstring support
    "sphinx.ext.viewcode",     # Link to highlighted source
]
```

### Documenting a Module

Create a `.md` or `.rst` file and use the `automodule`, `autoclass`, or `autofunction` directives:

~~~markdown
## API Reference

```{automodule} mypackage.core
:members:
:undoc-members:
:show-inheritance:
```
~~~

### Documenting Individual Items

~~~markdown
```{autofunction} mypackage.connect
```

```{autoclass} mypackage.EventEmitter
:members:
:special-members: __init__
```
~~~

### autodoc Options

```{list-table}
:header-rows: 1
:widths: 30 70

* - Option
  - Description
* - `:members:`
  - Include all public members.
* - `:undoc-members:`
  - Include members without docstrings.
* - `:private-members:`
  - Include `_private` members.
* - `:special-members:`
  - Include `__dunder__` methods (specify which, e.g., `__init__`).
* - `:show-inheritance:`
  - Show base classes.
* - `:inherited-members:`
  - Include members inherited from base classes.
* - `:exclude-members:`
  - Comma-separated list of members to skip.
```

:::{tip}
Combine autodoc with Napoleon for clean, readable docstrings. Write Google-style docstrings in your code and let Napoleon convert them to Sphinx format automatically.
:::
