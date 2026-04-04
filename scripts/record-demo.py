"""Record an animated GIF demo of the Lumina theme."""

import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_SRC = PROJECT_ROOT / "docs"
DOCS_OUT = PROJECT_ROOT / "docs" / "_build" / "html"
OUTPUT_GIF = PROJECT_ROOT / "docs" / "assets" / "demo.gif"

VIEWPORT = {"width": 1280, "height": 720}
GIF_WIDTH = 800
FPS = 10


def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print("Error: ffmpeg not found on PATH. Install it first:")
        print("  brew install ffmpeg    # macOS")
        print("  apt install ffmpeg     # Debian/Ubuntu")
        sys.exit(1)


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def build_docs():
    print("Building docs...")
    subprocess.run(
        ["uv", "run", "sphinx-build", str(DOCS_SRC), str(DOCS_OUT)],
        cwd=str(PROJECT_ROOT),
        check=True,
    )


def start_server(port):
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd=str(DOCS_OUT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base_url = f"http://localhost:{port}"
    for _ in range(50):
        try:
            urllib.request.urlopen(base_url)
            break
        except Exception:
            time.sleep(0.1)
    return server, base_url


def record_tour(base_url):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport=VIEWPORT,
            record_video_dir=str(PROJECT_ROOT / ".demo-tmp"),
            record_video_size=VIEWPORT,
        )
        page = context.new_page()

        # Ensure light mode start
        page.goto(f"{base_url}/getting-started/index.html")
        page.evaluate("localStorage.setItem('lumina-theme', 'light')")
        page.reload()
        page.wait_for_load_state("networkidle")

        # Pause to show light mode
        page.wait_for_timeout(1000)

        # Smooth scroll down
        page.evaluate("""
            new Promise(resolve => {
                const duration = 2000;
                const start = window.scrollY;
                const end = document.body.scrollHeight - window.innerHeight;
                const startTime = performance.now();
                function step(now) {
                    const elapsed = now - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    const ease = progress < 0.5
                        ? 2 * progress * progress
                        : -1 + (4 - 2 * progress) * progress;
                    window.scrollTo(0, start + (end - start) * ease);
                    if (progress < 1) requestAnimationFrame(step);
                    else resolve();
                }
                requestAnimationFrame(step);
            })
        """)
        page.wait_for_timeout(2000)

        # Pause at bottom
        page.wait_for_timeout(500)

        # Toggle dark mode
        page.click("[data-theme-toggle]")
        page.wait_for_timeout(1000)

        # Smooth scroll back up
        page.evaluate("""
            new Promise(resolve => {
                const duration = 2000;
                const start = window.scrollY;
                const startTime = performance.now();
                function step(now) {
                    const elapsed = now - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    const ease = progress < 0.5
                        ? 2 * progress * progress
                        : -1 + (4 - 2 * progress) * progress;
                    window.scrollTo(0, start * (1 - ease));
                    if (progress < 1) requestAnimationFrame(step);
                    else resolve();
                }
                requestAnimationFrame(step);
            })
        """)
        page.wait_for_timeout(2000)

        # Final pause
        page.wait_for_timeout(500)

        context.close()
        browser.close()

        # Find recorded video
        tmp_dir = PROJECT_ROOT / ".demo-tmp"
        videos = list(tmp_dir.glob("*.webm"))
        if not videos:
            print("Error: no video recorded")
            sys.exit(1)
        return videos[0]


def convert_to_gif(video_path):
    print("Converting to GIF...")
    OUTPUT_GIF.parent.mkdir(parents=True, exist_ok=True)
    palette = PROJECT_ROOT / ".demo-tmp" / "palette.png"

    # Pass 1: generate palette
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vf",
            f"fps={FPS},scale={GIF_WIDTH}:-1:flags=lanczos,palettegen=stats_mode=diff",
            str(palette),
        ],
        check=True,
        capture_output=True,
    )

    # Pass 2: create GIF with palette
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(palette),
            "-lavfi",
            f"fps={FPS},scale={GIF_WIDTH}:-1:flags=lanczos [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=5",
            "-loop",
            "0",
            str(OUTPUT_GIF),
        ],
        check=True,
        capture_output=True,
    )

    size_mb = OUTPUT_GIF.stat().st_size / (1024 * 1024)
    print(f"Created {OUTPUT_GIF} ({size_mb:.1f} MB)")


def cleanup():
    tmp_dir = PROJECT_ROOT / ".demo-tmp"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)


def main():
    check_ffmpeg()
    build_docs()

    port = find_free_port()
    server, base_url = start_server(port)

    try:
        video_path = record_tour(base_url)
        convert_to_gif(video_path)
    finally:
        server.terminate()
        server.wait(timeout=5)
        cleanup()

    print("Done!")


if __name__ == "__main__":
    main()
