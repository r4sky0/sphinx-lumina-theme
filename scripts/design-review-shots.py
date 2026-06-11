"""Capture screenshots of built docs for a design review.

Builds nothing itself — run ``uv run sphinx-build docs docs/_build/html`` first.
Output goes to ``.design-review/`` (gitignored). Set LUMINA_CHROMIUM to a
Chromium executable to override Playwright's managed browser.
"""

import http.server
import os
import threading

from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(__file__), "..", "docs", "_build", "html")
OUT = os.path.join(os.path.dirname(__file__), "..", ".design-review")
os.makedirs(OUT, exist_ok=True)

PAGES = [
    ("index.html", "home"),
    ("introduction.html", "introduction"),
    ("getting-started/index.html", "getting-started-hub"),
    ("getting-started/configuration.html", "configuration"),
    ("guides/navigation.html", "guide-navigation"),
    ("reference/admonitions.html", "ref-admonitions"),
    ("reference/code-blocks.html", "ref-code-blocks"),
    ("reference/cards-and-grids.html", "ref-cards"),
    ("reference/typography.html", "ref-typography"),
]


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, *args):
        pass


server = http.server.ThreadingHTTPServer(("127.0.0.1", 8901), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=os.environ.get("LUMINA_CHROMIUM") or None
    )

    for theme in ("light", "dark"):
        ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
        ctx.add_init_script(f"localStorage.setItem('lumina-theme', '{theme}')")
        page = ctx.new_page()
        for path, name in PAGES:
            page.goto(f"http://127.0.0.1:8901/{path}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(400)
            page.screenshot(path=os.path.join(OUT, f"{name}-{theme}.png"))
            # full-page shot for a few content-heavy pages
            if name in ("home", "ref-admonitions", "ref-typography", "configuration"):
                page.screenshot(
                    path=os.path.join(OUT, f"{name}-{theme}-full.png"), full_page=True
                )
        ctx.close()

    # mobile, light only
    ctx = browser.new_context(viewport={"width": 390, "height": 844})
    page = ctx.new_page()
    for path, name in [
        ("index.html", "home"),
        ("guides/navigation.html", "guide-navigation"),
    ]:
        page.goto(f"http://127.0.0.1:8901/{path}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(400)
        page.screenshot(path=os.path.join(OUT, f"{name}-mobile.png"))
    # open mobile menu
    page.goto("http://127.0.0.1:8901/index.html")
    page.wait_for_load_state("networkidle")
    btn = page.query_selector(
        "button[aria-label*='menu' i], button[aria-label*='navigation' i]"
    )
    if btn:
        btn.click()
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(OUT, "home-mobile-menu.png"))
    ctx.close()

    # search modal, desktop light
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    page = ctx.new_page()
    page.goto("http://127.0.0.1:8901/index.html")
    page.wait_for_load_state("networkidle")
    page.keyboard.press("Control+k")
    page.wait_for_timeout(500)
    page.keyboard.type("dark mode")
    page.wait_for_timeout(800)
    page.screenshot(path=os.path.join(OUT, "search-modal.png"))
    ctx.close()

    browser.close()

server.shutdown()
print("done:", len(os.listdir(OUT)), "screenshots in", OUT)
