"""Test admonition styling."""


def test_admonitions_render(index_html):
    """Admonitions should be present in the output."""
    admonitions = index_html.find_all(class_="admonition")
    assert len(admonitions) >= 4, (
        f"Expected at least 4 admonitions, got {len(admonitions)}"
    )


def test_note_admonition_has_type_class(index_html):
    """Note admonition should have both 'admonition' and 'note' classes."""
    note = index_html.find(class_="note")
    assert note is not None
    assert "admonition" in note.get("class", [])
