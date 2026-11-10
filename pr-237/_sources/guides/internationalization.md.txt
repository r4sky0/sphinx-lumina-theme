# Internationalization

Lumina's interface text — navigation labels, the search modal, copy buttons, the HTTP request editor, and screen-reader labels — follows your project's Sphinx `language` setting. Your page content is translated separately with Sphinx's own [internationalization workflow](https://www.sphinx-doc.org/en/master/usage/advanced/intl.html).

## Set the language

```{code-block} python
:caption: conf.py
language = "de"
```

Lumina ships translations for these languages:

| Code    | Language            |
| ------- | ------------------- |
| `ar`    | Arabic              |
| `de`    | German              |
| `es`    | Spanish             |
| `fr`    | French              |
| `ja`    | Japanese            |
| `zh_CN` | Simplified Chinese  |

Any other language falls back to English for Lumina's strings, while Sphinx still translates its own text. The page's `<html lang>` attribute and the Pagefind search index follow the same `language` value.

:::{note}
The bundled translations were drafted with machine assistance. Corrections from native speakers are welcome — see {doc}`/contributing/translations`.
:::

## Right-to-left languages

Lumina mirrors its layout automatically when `language` is a right-to-left language such as Arabic (`ar`), Hebrew (`he`), Persian (`fa`), or Urdu (`ur`). The page gets `<html dir="rtl">`, so the sidebar, table of contents, and directional icons switch sides. There is nothing else to configure.

Code blocks, inline code, API signatures, and HTTP request fields stay left to right. The `:align: left` and `:align: right` image options keep their literal meaning. Lumina's fonts have no Arabic or Hebrew glyphs, so that text uses the reader's system font.

When you add your own CSS, use logical properties such as `margin-inline-start` and `inset-inline-end` so it mirrors too. For anything that must differ, target `[dir="rtl"]`.

## Override a translation

To change a string for your project, add a catalog named `sphinx.po` to your own `locale_dirs`. Your catalog takes precedence over the one bundled with Lumina:

```{code-block} python
:caption: conf.py
language = "de"
locale_dirs = ["locale/"]
```

```{code-block} po
:caption: locale/de/LC_MESSAGES/sphinx.po
msgid "Copy as Markdown"
msgstr "Als Markdown übernehmen"
```

Sphinx compiles `sphinx.po` files in `locale_dirs` automatically on each build. Copy the message IDs from Lumina's template at `sphinx_lumina_theme/locale/sphinx.pot`.

The same approach adds a language Lumina doesn't ship. For a language that Sphinx itself has no translations for, Lumina's templates stay in English.

To fix or add a bundled translation, see {doc}`/contributing/translations`.
