"""Minimal Sphinx config for testing the Lumina theme."""

project = "Test Project"
extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
]
html_theme = "lumina"
html_theme_options = {
    "logo_icon": "hexagon",
    "nav_links": [
        {"title": "Guide", "url": "getting-started"},
        {"title": "GitHub", "url": "https://github.com/example/test", "external": True},
    ],
    "social_links": [
        {"icon": "github", "url": "https://github.com/example/test"},
    ],
    "source_repository": "https://github.com/example/test",
    "source_branch": "main",
    "source_directory": "docs/",
}
exclude_patterns = ["_build"]
myst_enable_extensions = ["colon_fence"]
