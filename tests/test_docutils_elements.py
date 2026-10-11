"""Docutils body elements are styled even though Lumina drops Sphinx's basic.css."""

import base64

import pytest
from conftest import sphinx_app
from playwright.sync_api import Page

PIXEL = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)

INDEX = """\
Elements
========

.. sidebar:: Sidebar title

   Sidebar body.

.. topic:: Topic title

   Topic body.

.. rubric:: A rubric

.. centered:: Centered text

.. image:: pixel.png
   :align: right
   :width: 40px

Inline |pixel| image.

.. |pixel| image:: pixel.png

| Line one
|     Nested line

Term : classifier
   Definition.

.. versionremoved:: 1.0
   Gone.

.. productionlist::
   rule: "a" | "b"

Footnote [#f]_.

.. [#f] The footnote.

=====  =========================
A      body row with several words
=====  =========================

Section
-------

Body.
"""


@pytest.fixture(scope="module")
def elements_page(tmp_path_factory):
    src = tmp_path_factory.mktemp("docutils_src")
    (src / "conf.py").write_text('project = "Elements"\nhtml_theme = "lumina"\n')
    (src / "index.rst").write_text(INDEX)
    (src / "pixel.png").write_bytes(PIXEL)
    out = tmp_path_factory.mktemp("docutils_build")
    sphinx_app(src, out).build()
    return (out / "index.html").as_uri()


def style(page: Page, selector: str, prop: str, pseudo: str | None = None) -> str:
    return page.locator(f".lumina-article {selector}").first.evaluate(
        "(el, [prop, pseudo]) => getComputedStyle(el, pseudo)[prop]", [prop, pseudo]
    )


def test_docutils_elements_are_styled(page: Page, elements_page: str):
    page.set_viewport_size({"width": 1280, "height": 900})
    page.goto(elements_page)

    assert style(page, "aside.sidebar", "float") == "right"
    assert style(page, "img.align-right", "float") == "right"
    assert style(page, "aside.topic", "borderTopStyle") == "solid"
    assert style(page, "p.rubric", "fontWeight") == "600"
    assert style(page, "p.centered", "textAlign") == "center"
    assert style(page, "p img", "display") == "inline-block"
    assert style(page, ".line-block .line-block", "marginLeft") != "0px"
    assert style(page, "dt .classifier", "content", "::before") == '":"'
    assert style(page, "div.versionremoved", "borderLeftStyle") == "solid"
    assert style(page, "pre:has(> strong)", "overflowX") == "auto"
    assert style(page, "aside.footnote > span.label", "float") == "left"
    assert style(page, "td", "hyphens") == "none"
    assert style(page, "section > h2", "clear") == "both"


def test_floats_stack_on_narrow_screens(page: Page, elements_page: str):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(elements_page)

    assert style(page, "aside.sidebar", "float") == "none"
    assert style(page, "img.align-right", "float") == "none"
