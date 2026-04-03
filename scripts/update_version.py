"""Update version references in docs during semantic-release.

Called by python-semantic-release via build_command after the version
is bumped but before the release commit is created.

Usage: python scripts/update_version.py <version>
"""

import re
import subprocess
import sys
from pathlib import Path

DOCS_FILES = [
    "README.md",
]

PATTERNS = [
    # Git install URLs: ...sphinx-lumina-theme.git@v1.2.3 or @v{version}
    (
        re.compile(r"sphinx-lumina-theme\.git@v(?:[\d]+\.[\d]+\.[\d]+|\{version\})"),
        "sphinx-lumina-theme.git@v{version}",
    ),
]


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <version>", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]
    root = Path(__file__).resolve().parent.parent

    for filename in DOCS_FILES:
        path = root / filename
        text = path.read_text()
        new_text = text
        for pattern, template in PATTERNS:
            new_text = pattern.sub(template.format(version=version), new_text)
        if text != new_text:
            path.write_text(new_text)
            print(f"Updated {filename} → v{version}")
        else:
            print(f"No changes in {filename}")

    subprocess.run(
        ["git", "add", *DOCS_FILES],
        cwd=root,
        check=True,
    )


if __name__ == "__main__":
    main()
