"""Tests for right-to-left language support."""

import pytest
from bs4 import BeautifulSoup
from conftest import build_translated_site

from sphinx_lumina_theme import _is_rtl


@pytest.mark.parametrize("language", ["ar", "he", "fa", "ur", "fa_IR", "ar-EG"])
def test_rtl_languages_are_detected(language):
    assert _is_rtl(language)


@pytest.mark.parametrize("language", ["en", "de", "zh_CN", "sr@latin", "xx", "", None])
def test_other_languages_stay_ltr(language):
    assert not _is_rtl(language)


def test_rtl_build_sets_dir_and_keeps_html_attributes(tmp_path):
    out = build_translated_site(tmp_path, "ar")
    html = BeautifulSoup((out / "other.html").read_text(), "html.parser").html
    assert html["dir"] == "rtl"
    assert html["lang"] == "ar"
    assert html["data-content_root"] == "./"


def test_ltr_build_has_no_dir(index_html):
    assert not index_html.html.has_attr("dir")
