---
description: "How Lumina handles SEO and social-share metadata, plus per-page overrides and opt-out controls."
---

# SEO and discoverability

Lumina automatically emits a complete set of SEO and social-share metadata. As long as you set `html_baseurl` in your `conf.py`, you get:

- `<meta name="description">` with smart fallbacks
- `<link rel="canonical">` on every page
- Open Graph tags (`og:title`, `og:description`, `og:image` (with optional `width`/`height`), `og:type`, `og:url`, `og:site_name`, `og:locale`)
- Twitter Card tags (`twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`, `twitter:site`)
- JSON-LD structured data (`BreadcrumbList`, `TechArticle` with ISO 8601 dates and a Google-conformant `publisher.logo`, `WebSite` + `SearchAction`)
- A generated `sitemap.xml` — with per-URL `<lastmod>` when `sphinx_last_updated_by_git` is loaded
- A default `robots.txt` pointing at the sitemap

Everything is on by default. There's no enable flag.

## Required: `html_baseurl`

Canonical URLs, sitemap entries, and the `robots.txt` `Sitemap:` line all need an absolute site URL. Set `html_baseurl` in `conf.py`:

```python
html_baseurl = "https://docs.example.com/"
```

If you don't set this, Lumina logs one warning at the start of the build and skips the URL-dependent features. The rest (description, OG title, Twitter card, etc.) still work.

## Configuring social cards

Set a sitewide Open Graph image — the picture that appears when your docs are shared on Slack, Twitter/X, LinkedIn, etc.

```python
html_theme_options = {
    "og_image": "og-card.png",  # filename in _static/, OR an absolute URL
    "og_image_alt": "MyProject — distributed task queue",
    "og_image_width": "1200",   # match your card; helps Slack/Facebook render instantly
    "og_image_height": "630",
    "twitter_site": "@myproject",  # optional; falls back to social_links
}
```

Aim for a 1200×630 PNG. Keep your logo and a short tagline in the top-left third (Twitter crops the right edge in some layouts). Declaring `og_image_width` / `og_image_height` lets Facebook, LinkedIn, and Slack reserve the slot before the image loads, so the preview never flashes a broken thumbnail.

## Publisher logo (Rich Results)

Lumina's `TechArticle` JSON-LD includes a `publisher.logo` for Google Rich Results. **The publisher logo is not the same as `og_image`** — Google requires it to be near-square (think 60×60 to 600×60), while a social card is a 1200×630 banner. Reusing the social card as a publisher logo can disqualify your page from Rich Results.

Ship a small square logo and point Lumina at it:

```python
html_theme_options = {
    "publisher_logo": "logo-square.png",  # filename in _static/, or absolute URL
}
```

The fallback chain is: `publisher_logo` → `html_logo` (when raster) → omit `publisher.logo` entirely (better to omit than to lie to Google).

## Sitemap `<lastmod>`

When [`sphinx_last_updated_by_git`](/extensions/sphinx-last-updated-by-git) is in your `extensions` list, Lumina automatically flips `sitemap_show_lastmod = True` so every URL in `sitemap.xml` carries the file's last-commit date. `<lastmod>` is the strongest single signal Google uses to schedule recrawls — adding it makes content updates show up in search faster.

```python
extensions = [
    # ...
    "sphinx_last_updated_by_git",
]
```

If you've explicitly set `sitemap_show_lastmod` (in `conf.py` or via `-D`), Lumina respects your choice.

## Per-page overrides via front matter

Any MyST page can override the defaults:

```markdown
---
description: "Bypass the auto-extracted description with this exact text."
og_image: "custom-card.png"
og_type: "article"  # or "website"
keywords: "comma, separated, terms"
noindex: true       # hide from search engines and exclude from sitemap.xml
---

# Page title
```

All keys are optional.

## Opting out

To turn off all SEO emission (no meta tags, no JSON-LD, no sitemap, no robots.txt):

```python
html_theme_options = {
    "disable_seo": "true",
}
```

This is for niche cases — internal-only sites that don't want to leak structured data, intranet portals, etc.

## Replacing `robots.txt`

Lumina only writes `robots.txt` if one isn't already at the build root. Drop your own into a directory and point `html_extra_path` at it:

```python
html_extra_path = ["public"]   # public/robots.txt will win
```

## How descriptions are picked

For each page, in priority order:

1. `description` from front matter
2. The first paragraph in the page (≥ 30 chars, skipping admonitions, code blocks, and toctrees), truncated to ~160 chars
3. `html_short_title` (or `project`)

If none of those produce a usable string, no description meta is emitted (rather than ship a misleading default).

## Verifying what's emitted

After building, view the page source of `_build/html/index.html` (or any built page) and search for `og:` and `application/ld+json` to see the rendered output. Online validators worth a glance:

- [Twitter Card validator](https://cards-dev.twitter.com/validator)
- [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
- [Google Rich Results Test](https://search.google.com/test/rich-results) — for the JSON-LD schemas
