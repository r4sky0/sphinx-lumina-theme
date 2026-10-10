# sphinx-last-updated-by-git

[sphinx-last-updated-by-git](https://github.com/mgeier/sphinx-last-updated-by-git) adds a “Last updated” date to each page, pulled from git commit history. Lumina displays it automatically in the page footer when the extension is active.

## Setup

```bash
uv add sphinx-last-updated-by-git
```

```python
extensions = ["sphinx_last_updated_by_git"]

html_last_updated_fmt = "%B %-d, %Y"  # e.g. "April 3, 2025"
```

The date appears in the footer of every page that has a git history. Pages without a commit history (new, untracked files) show nothing.

## CI: Full Clone Required

By default, GitHub Actions performs a shallow clone (`fetch-depth: 1`). This causes the extension to return no date for most pages. Set `fetch-depth: 0` in your checkout step:

```yaml
- uses: actions/checkout@v6
  with:
    fetch-depth: 0
```

## Suppressing Warnings

If you build in shallow-clone environments (e.g., local preview builds), suppress the warning:

```python
suppress_warnings = ["git.too_shallow"]
```

## Configuration Reference

| Option                         | Default   | Description                                                         |
|--------------------------------|-----------|---------------------------------------------------------------------|
| `html_last_updated_fmt`        | `None`    | Date format string (strftime syntax). Required to display the date. |
| `git_last_updated_metatags`    | `True`    | Inject `<meta>` tags with the timestamp into `<head>`.              |
| `git_exclude_commits`          | `[]`      | Commit hashes to ignore (useful after mass-reformatting commits).   |
| `git_last_updated_when_merged` | `False`   | Use merge date instead of author date.                              |
