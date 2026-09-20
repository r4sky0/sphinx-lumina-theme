"""Reading metadata uses the document structure, not client-side relocation."""

from types import SimpleNamespace

import pytest
from docutils import nodes
from docutils.utils import new_document
from sphinx_lumina_theme import _insert_reading_time


@pytest.mark.parametrize("intro", [True, False])
@pytest.mark.parametrize("override", ["12", "false"])
def test_reading_time_placement_and_override(intro, override):
    tree = new_document("test")
    section = nodes.section()
    section += nodes.title(text="Page title")
    if intro:
        section += nodes.paragraph(text="An introduction.")
    section += nodes.section("", nodes.title(text="First section"))
    tree += section
    app = SimpleNamespace(
        builder=SimpleNamespace(
            format="html", theme_options={"show_reading_time": "true"}
        ),
        env=SimpleNamespace(metadata={"test": {"reading_time": override}}),
    )

    _insert_reading_time(app, tree, "test")

    if override == "false":
        assert not list(tree.findall(nodes.raw))
    else:
        metadata = section[2 if intro else 1]
        assert isinstance(metadata, nodes.raw)
        assert "12 min read" in metadata.astext()
        assert 'aria-hidden="true"' in metadata.astext()
