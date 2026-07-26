#!/usr/bin/env python3
"""Validate every executable BUILD-1 acceptance gate."""

from __future__ import annotations

import compileall
import importlib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "pyproject.toml", "README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md", "SECURITY.md", "Makefile", ".gitignore", ".editorconfig",
    ".gitattributes", ".github/workflows/ci.yml", ".github/PULL_REQUEST_TEMPLATE.md",
    "config/example.toml", "docs/architecture.md", "docs/build-1-acceptance.md",
    "docs/configuration.md", "docs/health.md", "docs/kernel-lifecycle.md", "docs/testing.md",
    "scripts/run_demo.py", "scripts/validate_build1.py", "src/developeros/__init__.py",
    "src/developeros/__main__.py", "src/developeros/core/api.py",
    "src/developeros/core/bootstrap.py", "src/developeros/core/configuration.py",
    "src/developeros/core/container.py", "src/developeros/core/diagnostics.py",
    "src/developeros/core/errors.py", "src/developeros/core/health.py",
    "src/developeros/core/kernel.py", "src/developeros/core/lifecycle.py",
    "src/developeros/core/logging.py", "src/developeros/core/version.py",
}


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    if sys.version_info < (3, 11):
        raise SystemExit("Python 3.11 or newer is required")
    missing = sorted(path for path in REQUIRED if not (ROOT / path).is_file())
    if missing:
        raise SystemExit(f"Missing required files: {', '.join(missing)}")
    sys.path.insert(0, str(ROOT / "src"))
    importlib.import_module("developeros.core.api")
    if not compileall.compile_dir(ROOT / "src", quiet=1):
        raise SystemExit("Python compilation failed")
    for tool in ("pytest", "ruff", "mypy"):
        if shutil.which(tool) is None:
            raise SystemExit(f"Required validation tool is not installed: {tool}")
    run(["pytest"])
    run(["ruff", "check", "."])
    run(["mypy", "src/developeros"])
    print("DeveloperOS BUILD-1 validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
