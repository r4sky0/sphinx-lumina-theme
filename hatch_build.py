import shutil
import subprocess
import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class BuildAssetsHook(BuildHookInterface):
    """Build CSS and JS assets with pnpm before packaging."""

    def initialize(self, version, build_data):
        if not shutil.which("pnpm"):
            sys.exit("[hatch] pnpm is required to build assets — install it first")

        self._run(["pnpm", "install", "--frozen-lockfile"])
        self._run(["pnpm", "run", "build"])

    def _run(self, cmd):
        result = subprocess.run(cmd, cwd=self.root)
        if result.returncode != 0:
            sys.exit(f"[hatch] Command failed: {' '.join(cmd)}")
