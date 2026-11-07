"""Lumina's own Pygments styles, used by the ``lumina`` ``code_style`` preset.

Colors mirror the default emerald tokens in ``base.css`` (Pygments needs literal
hex values, so they do not follow ``accent_color``). Every token clears 4.5:1
on its code background.
"""

from pygments.style import Style
from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
    Whitespace,
)


def _styles(text, muted, keyword, string, number, error):
    return {
        Text: text,
        Whitespace: "",
        Error: error,
        Comment: muted,
        Comment.Preproc: keyword,
        Keyword: keyword,
        Keyword.Type: number,
        Operator: text,
        Operator.Word: keyword,
        Punctuation: muted,
        Name: text,
        Name.Builtin: number,
        Name.Function: f"bold {text}",
        Name.Class: f"bold {text}",
        Name.Decorator: keyword,
        Name.Exception: f"bold {text}",
        Name.Tag: keyword,
        Name.Attribute: number,
        Name.Label: keyword,
        String: string,
        String.Escape: number,
        String.Interpol: number,
        Number: number,
        Generic.Deleted: error,
        Generic.Inserted: keyword,
        Generic.Heading: f"bold {text}",
        Generic.Subheading: f"bold {muted}",
        Generic.Prompt: f"bold {muted}",
        Generic.Output: muted,
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Generic.Error: error,
    }


class LuminaLightStyle(Style):
    """Emerald keywords, warm strings and quiet punctuation on ``--lumina-code-bg``."""

    name = "lumina-light"
    background_color = "#f6f7f6"
    highlight_color = "#eaf6ef"
    line_number_color = "#59635e"
    styles = _styles(
        text="#202624",
        muted="#59635e",
        keyword="#047857",
        string="#9a3412",
        number="#0e7490",
        error="#b91c1c",
    )


class LuminaDarkStyle(Style):
    """Dark counterpart of :class:`LuminaLightStyle`."""

    name = "lumina-dark"
    background_color = "#1b211e"
    highlight_color = "#1c3329"
    line_number_color = "#a8b5ac"
    styles = _styles(
        text="#e9eeeb",
        muted="#a8b5ac",
        keyword="#5ed9a3",
        string="#fdba74",
        number="#67e8f9",
        error="#fca5a5",
    )
