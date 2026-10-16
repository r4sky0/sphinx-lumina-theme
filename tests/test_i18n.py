"""Tests for translated theme UI strings."""

import json
import re
from pathlib import Path

import pytest
from babel.messages.extract import extract_from_dir
from babel.messages.mofile import read_mo
from babel.messages.pofile import read_po
from bs4 import BeautifulSoup
from conftest import sphinx_app
from sphinx import locale

PACKAGE = Path(__file__).parent.parent / "src" / "sphinx_lumina_theme"
LOCALE = PACKAGE / "locale"
I18N_TEMPLATE = PACKAGE / "theme" / "components" / "i18n.html"
PLACEHOLDER = re.compile(r"\{\w+\}|%\(\w+\)s")


def _site(tmp_path, language):
    src = tmp_path / "src"
    src.mkdir()
    (src / "conf.py").write_text(
        'project = "I18n"\nhtml_theme = "lumina"\n'
        'html_theme_options = {"show_reading_time": "true"}\n'
        f"language = {language!r}\n"
    )
    (src / "index.rst").write_text(
        "Home\n====\n\nIntro.\n\nPart\n----\n\nText.\n\n.. toctree::\n\n   other\n"
    )
    (src / "other.rst").write_text("Other\n=====\n\nText.\n")
    locale.translators.clear()  # Sphinx keeps catalogs in module-global state.
    try:
        sphinx_app(src, tmp_path / "out").build()
    finally:
        locale.translators.clear()
    return BeautifulSoup((tmp_path / "out" / "index.html").read_text(), "html.parser")


@pytest.fixture(scope="module")
def german(tmp_path_factory):
    return _site(tmp_path_factory.mktemp("i18n_de"), "de")


def test_templates_render_translated_strings(german):
    assert german.select_one(".lumina-skip-link").get_text() == "Zum Inhalt springen"
    assert (
        "Weiter" in german.select_one("nav[aria-label='Seitennavigation']").get_text()
    )
    assert "Auf dieser Seite" in german.select_one("#lumina-toc").get_text()
    assert german.find(attrs={"aria-label": "Farbschema umschalten"}) is not None


def test_reading_time_is_translated(german):
    assert "Min. Lesezeit" in german.select_one(".lumina-reading-time").get_text()


def test_js_catalog_is_emitted_for_non_english(german):
    catalog = json.loads(german.select_one("#lumina-i18n").string)
    assert catalog["Copied!"] == "Kopiert!"
    assert catalog["{visible} of {total} rows"] == "{visible} von {total} Zeilen"


def test_js_catalog_is_omitted_for_english(tmp_path):
    assert _site(tmp_path, "en").select_one("#lumina-i18n") is None


def test_every_js_key_is_in_the_catalog_template():
    listed = set(re.findall(r"'([^']+)': _\('\1'\)", I18N_TEMPLATE.read_text()))
    used = set()
    files = [
        *(PACKAGE / "_static_src" / "js").rglob("*.js"),
        *(PACKAGE / "theme").rglob("*.html"),
    ]
    for path in files:
        if path != I18N_TEMPLATE:
            used |= set(
                re.findall(r"""\bt\((?:"([^"]+)"|'([^']+)')""", path.read_text())
            )
    used = {double or single for double, single in used}
    assert used - listed == set(), "add these keys to components/i18n.html"


def test_template_is_current():
    method_map = [("**.py", "python"), ("**/theme/**.html", "jinja2.ext:babel_extract")]
    extracted = {
        message for _, _, message, _, _ in extract_from_dir(PACKAGE, method_map)
    }
    with open(LOCALE / "sphinx.pot", "rb") as f:
        template = {message.id for message in read_po(f) if message.id}
    assert extracted == template, "run `pnpm run i18n`"


@pytest.mark.parametrize(
    "po_path", sorted(LOCALE.glob("*/LC_MESSAGES/sphinx.po")), ids=lambda p: p.parts[-3]
)
def test_catalog_is_compiled_and_keeps_placeholders(po_path):
    with open(po_path, "rb") as f:
        po = {m.id: m.string for m in read_po(f) if m.id and m.string and not m.fuzzy}
    with open(po_path.with_suffix(".mo"), "rb") as f:
        mo = {m.id: m.string for m in read_mo(f) if m.id}
    assert po == mo, "run `pnpm run i18n` to recompile"
    for msgid, msgstr in po.items():
        assert sorted(PLACEHOLDER.findall(msgstr)) == sorted(
            PLACEHOLDER.findall(msgid)
        ), msgid
        # Template strings are inserted into HTML attributes without escaping.
        assert not set('<>&"') & (set(msgstr) - set(msgid)), msgid
