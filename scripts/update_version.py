"""Update version references in docs during semantic-release."""

import re
import subprocess
import sys
from pathlib import Path

version = sys.argv[1]
root = Path(__file__).resolve().parent.parent
pattern = re.compile(r"@v(?:[\d]+\.[\d]+\.[\d]+|\{version\}|\{\{version\}\})")

paths = [root / "README.md", root / "docs" / "getting-started.md"]

for path in paths:
    text = path.read_text()
    text = pattern.sub(f"@v{version}", text)
    path.write_text(text)

subprocess.run(["git", "add", *[str(p) for p in paths]], cwd=root, check=True)
