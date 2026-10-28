# Internationalization

Lumina’s interface text — navigation labels, the search modal, copy buttons, the HTTP request editor, and screen-reader labels — follows your project’s Sphinx `language` setting. Your page content is translated separately with Sphinx’s own [internationalization workflow](https://www.sphinx-doc.org/en/master/usage/advanced/intl.html).

## Set the language

```python
language = "de"
```

Lumina ships translations for these languages:

| Code    | Language           |
|---------|--------------------|
| `de`    | German             |
| `es`    | Spanish            |
| `fr`    | French             |
| `ja`    | Japanese           |
| `zh_CN` | Simplified Chinese |

Any other language falls back to English for Lumina’s strings, while Sphinx still translates its own text. The page’s `<html lang>` attribute and the Pagefind search index follow the same `language` value.

#### NOTE
The bundled translations were drafted with machine assistance. Corrections from native speakers are welcome — see [Translations](../contributing/translations.md).

## Override a translation

To change a string for your project, add a catalog named `sphinx.po` to your own `locale_dirs`. Your catalog takes precedence over the one bundled with Lumina:

```python
language = "de"
locale_dirs = ["locale/"]
```

```po
msgid "Copy as Markdown"
msgstr "Als Markdown übernehmen"
```

Sphinx compiles `sphinx.po` files in `locale_dirs` automatically on each build. Copy the message IDs from Lumina’s template at `sphinx_lumina_theme/locale/sphinx.pot`.

The same approach adds a language Lumina doesn’t ship. For a language that Sphinx itself has no translations for, Lumina’s templates stay in English.

To fix or add a bundled translation, see [Translations](../contributing/translations.md).
