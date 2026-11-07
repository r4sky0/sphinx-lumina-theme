# Translations

How to fix or add a bundled translation, and how to make new interface text translatable. For setting a site's language, see {doc}`/guides/internationalization`.

## Contributing a translation

Lumina's catalogs live in `src/sphinx_lumina_theme/locale/<language>/LC_MESSAGES/sphinx.po`.

1. For a new language, create its catalog from the template:

   ```console
   $ uv run pybabel init -i src/sphinx_lumina_theme/locale/sphinx.pot -d src/sphinx_lumina_theme/locale -D sphinx -l pt_BR
   ```

2. Fill in each `msgstr`. Keep placeholders such as `{count}` and `%(minutes)s` unchanged, and don't use `<`, `>`, `&`, or straight double quotes — use the typographic quotes of your language instead.
3. Run `pnpm run i18n` to refresh the template and compile the `.mo` files, then commit both the `.po` and `.mo` files.
4. Add the language to the table in {doc}`/guides/internationalization`.

### Adding translatable strings

When you add interface text to the theme:

- In templates, wrap it as `{{ _("Text") }}`.
- In JavaScript, call `t("Text")` from `utils/i18n.js`. In Alpine expressions, use the `$t('Text')` magic. Placeholders use braces: `t("{count} rows", { count })`.
- List every JavaScript string in `theme/components/i18n.html`, which emits the translated strings for non-English builds.

Then run `pnpm run i18n`. `tests/test_i18n.py` fails when a JavaScript string is missing from `i18n.html`, the template is stale, or a `.mo` file doesn't match its `.po` file.
