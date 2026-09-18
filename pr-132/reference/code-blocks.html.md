# Code Blocks

Syntax-highlighted code with line numbers, emphasis, captions, and more.

## Basic Syntax Highlighting

Specify the language after the opening fence for syntax highlighting.

### Python

```python
def fibonacci(n: int) -> list[int]:
    """Generate the first n Fibonacci numbers."""
    sequence = []
    a, b = 0, 1
    for _ in range(n):
        sequence.append(a)
        a, b = b, a + b
    return sequence
```

### JavaScript

```javascript
async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}
```

### Rust

```rust
fn binary_search<T: Ord>(slice: &[T], target: &T) -> Option<usize> {
    let mut low = 0;
    let mut high = slice.len();
    while low < high {
        let mid = low + (high - low) / 2;
        match slice[mid].cmp(target) {
            std::cmp::Ordering::Equal => return Some(mid),
            std::cmp::Ordering::Less => low = mid + 1,
            std::cmp::Ordering::Greater => high = mid,
        }
    }
    None
}
```

### Bash

```bash
#!/bin/bash
for file in *.md; do
    echo "Processing: $file"
    wc -w "$file"
done
```

### YAML

```yaml
server:
  host: 0.0.0.0
  port: 8080
  debug: false

database:
  url: postgresql://localhost/mydb
  pool_size: 5
```

### JSON

```json
{
  "name": "sphinx-lumina-theme",
  "version": "0.1.0",
  "dependencies": {
    "sphinx": ">=7.0"
  }
}
```

### HTML

```html
<nav class="sidebar" role="navigation" aria-label="Main">
  <ul>
    <li><a href="/">Home</a></li>
    <li><a href="/docs">Documentation</a></li>
  </ul>
</nav>
```

### CSS

```css
:root {
  --color-accent: #10b981;
  --color-bg: #fcfcfc;
  --color-text: #18181b;
}

.admonition {
  border-left: 3px solid var(--color-accent);
  padding: 1rem;
}
```

### TOML

```toml
[project]
name = "my-project"
version = "1.0.0"
requires-python = ">=3.12"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

## Line Numbers

Add `:linenos:` to display line numbers alongside the code.

```python
class EventEmitter:
    def __init__(self):
        self._handlers = {}

    def on(self, event: str, handler):
        self._handlers.setdefault(event, []).append(handler)

    def emit(self, event: str, *args, **kwargs):
        for handler in self._handlers.get(event, []):
            handler(*args, **kwargs)
```

The MyST syntax:

```markdown
```{code-block} python
:linenos:
your code here
```
```

## Line Emphasis

Highlight specific lines to draw attention to important parts.

```python
def connect(host, port, retries=3):
    for attempt in range(retries):
        try:
            return socket.create_connection((host, port))
        except ConnectionError:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
```

The MyST syntax:

```markdown
```{code-block} python
:linenos:
:emphasize-lines: 3,4,5
your code here
```
```

## Captions

Add a caption above the code block to describe its purpose.

```python
html_theme = "lumina"
html_theme_options = {
    "accent_color": "#10b981",
}
```

The MyST syntax:

```markdown
```{code-block} python
:caption: conf.py — Minimal theme configuration
your code here
```
```

## Diff Highlighting

Use the `diff` language to show additions and removals.

```diff
- html_theme = "alabaster"
+ html_theme = "lumina"
+ html_theme_options = {
+     "accent_color": "#10b981",
+ }
```

## Tabbed Code Blocks

Group related code in tabs using sphinx-design. Useful for showing the same concept in multiple languages.

### Python

```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

### JavaScript

```javascript
function hello(name) {
  return `Hello, ${name}!`;
}
```

### Rust

```rust
fn hello(name: &str) -> String {
    format!("Hello, {}!", name)
}
```

The MyST syntax:

```markdown
::::{tab-set}
:::{tab-item} Python
```python
code here
```
:::
:::{tab-item} JavaScript
```javascript
code here
```
:::
::::
```

## Including Code from Files

The `literalinclude` directive pulls code directly from a file in your project. This keeps examples in sync with real code.

```python
"""Sphinx-Lumina-Theme documentation."""

from sphinx_lumina_theme import __version__

project = "Sphinx Lumina Theme"
extensions = [
    "myst_parser",
    "sphinx_design",
```

The MyST syntax:

```markdown
```{literalinclude} ../path/to/file.py
:language: python
:caption: path/to/file.py
```
```

### Useful Options

| Option              | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `:language:`        | Syntax highlighting language. Auto-detected from file extension if omitted. |
| `:lines:`           | Include only specific lines. Examples: `1-10`, `5,8,12`, `1-5,10-15`.       |
| `:linenos:`         | Show line numbers.                                                          |
| `:emphasize-lines:` | Highlight specific lines within the included range.                         |
| `:caption:`         | Add a caption above the code block.                                         |
| `:start-after:`     | Include content after a matching string (exclusive).                        |
| `:end-before:`      | Include content before a matching string (exclusive).                       |

## Copy Button

All code blocks include a copy-to-clipboard button provided by `sphinx-copybutton`. Hover over any code block to see it appear in the top-right corner. No configuration needed — it works automatically.

## Wrap Long Lines

A “wrap long lines” toggle appears alongside the copy button on every code block. Click it to wrap the current block — useful for long URLs, single-line shell commands, or any code that overflows horizontally. The toggle is per-block: turning wrap on for one block leaves the others unchanged.

Disable site-wide with `code_wrap_toggle = "false"` in `html_theme_options` — see [Configuration](../getting-started/configuration.md).

## Quick Reference

| Feature            | Directive              | Key option                   |
|--------------------|------------------------|------------------------------|
| Basic highlighting | Fenced code block      | Language after opening fence |
| Line numbers       | `code-block`           | `:linenos:`                  |
| Line emphasis      | `code-block`           | `:emphasize-lines: 3,4,5`    |
| Caption            | `code-block`           | `:caption: text`             |
| Include from file  | `literalinclude`       | `:lines: 1-10`               |
| Diff view          | Fenced code block      | `diff` language              |
| Tabbed code        | `tab-set` + `tab-item` | sphinx-design directives     |
