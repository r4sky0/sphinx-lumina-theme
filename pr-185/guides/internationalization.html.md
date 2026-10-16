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
The bundled translations were drafted with machine assistance. Corrections from native speakers are welcome — see [Contributing a translation](#i18n-contributing).

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

<a id="i18n-contributing"></a>

## Contributing a translation

Lumina’s catalogs live in `src/sphinx_lumina_theme/locale/<language>/LC_MESSAGES/sphinx.po`.

1. For a new language, create its catalog from the template:
   ```console
   $ uv run pybabel init -i src/sphinx_lumina_theme/locale/sphinx.pot -d src/sphinx_lumina_theme/locale -D sphinx -l pt_BR
   ```
2. Fill in each `msgstr`. Keep placeholders such as `{count}` and `%(minutes)s` unchanged, and don’t use `<`, `>`, `&`, or straight double quotes — use the typographic quotes of your language instead.
3. Run `pnpm run i18n` to refresh the template and compile the `.mo` files, then commit both the `.po` and `.mo` files.
4. Add the language to the table above.

### Adding translatable strings

When you add interface text to the theme:

- In templates, wrap it as `{{ _("Text") }}`.
- In JavaScript, call `t("Text")` from `utils/i18n.js`. In Alpine expressions, use the `$t('Text')` magic. Placeholders use braces: `t("{count} rows", { count })`.
- List every JavaScript string in `theme/components/i18n.html`, which emits the translated strings for non-English builds.

Then run `pnpm run i18n`. `tests/test_i18n.py` fails when a JavaScript string is missing from `i18n.html`, the template is stale, or a `.mo` file doesn’t match its `.po` file.
