"""Sphinx-Lumina-Theme documentation."""

from sphinx_lumina_theme import __version__

project = "Sphinx Lumina Theme"
extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinxcontrib.mermaid",
    "sphinxcontrib.openapi",
    "sphinx_llm.txt",
    "sphinx_last_updated_by_git",
    "sphinx_js",
]

# sphinx-js configuration
js_source_path = "../src/sphinx_lumina_theme/_static_src/js"
jsdoc_config_path = "../jsdoc.json"
html_last_updated_fmt = "%B %-d, %Y"
suppress_warnings = ["git.too_shallow"]
myst_enable_extensions = [
    "colon_fence",
    "amsmath",
    "dollarmath",
    "tasklist",
    "deflist",
    "fieldlist",
    "substitution",
]
html_theme = "lumina"
html_baseurl = "https://r4sky0.github.io/sphinx-lumina-theme/"
html_theme_options = {
    "source_repository": "https://github.com/r4sky0/sphinx-lumina-theme",
    "source_branch": "main",
    "source_directory": "docs/",
    "social_links": [
        {"icon": "github", "url": "https://github.com/r4sky0/sphinx-lumina-theme"},
    ],
    "api_base_url": "https://petstore3.swagger.io/api/v3",
    "wide_layout": "toggle",
    "show_reading_time": "true",
    "image_lightbox": "true",
    "og_image": "og-card.png",
    "og_image_alt": "Sphinx Lumina Theme — modern documentation theme with dark mode",
    "og_image_width": "1200",
    "og_image_height": "630",
    "publisher_logo": "logo-square.png",
    "announcement": 'A fast, modern Sphinx theme with dark mode, full-text search, and Alpine.js interactivity. <a href="https://github.com/r4sky0/sphinx-lumina-theme">Star on GitHub ★</a>',
    "doc_sections": [
        {
            "name": "User Documentation",
            "description": "Installation, guides & reference",
            "icon": "book-open",
            "color": "#10b981",
            "default": True,
            "link": "getting-started/index",
        },
        {
            "path": "contributing",
            "name": "Developer Documentation",
            "description": "Architecture & development",
            "icon": "code",
            "color": "#8b5cf6",
        },
    ],
}
exclude_patterns = ["_build", "superpowers"]
templates_path = ["_templates"]
html_static_path = ["_static"]
myst_substitutions = {
    "project_name": "Sphinx Lumina Theme",
    "version": __version__,
}


def _replace_version_placeholder(_app, _docname, source):
    source[0] = source[0].replace("@v{version}", f"@v{__version__}")


def setup(app):
    app.connect("source-read", _replace_version_placeholder)
