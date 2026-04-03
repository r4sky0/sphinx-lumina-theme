"""Sphinx-Lumina-Theme documentation."""

from sphinx_lumina_theme import __version__

project = "Sphinx Lumina Theme"
extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinxcontrib.mermaid",
]
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
html_theme_options = {
    "source_repository": "https://github.com/r4sky0/sphinx-lumina-theme",
    "source_branch": "main",
    "source_directory": "docs/",
    "social_links": [
        {"icon": "github", "url": "https://github.com/r4sky0/sphinx-lumina-theme"},
    ],
}
exclude_patterns = ["_build", "superpowers"]
templates_path = ["_templates"]
html_static_path = ["_static"]
myst_substitutions = {
    "project_name": "Sphinx Lumina Theme",
    "version": __version__,
}
