#!/usr/bin/env python3
"""Run the complete DeveloperOS BUILD-1 demonstration."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from developeros.core.bootstrap import bootstrap  # noqa: E402
from developeros.core.diagnostics import collect_diagnostics  # noqa: E402


def main() -> int:
    """Load configuration, run the kernel, print health and diagnostics, then stop."""

    kernel = bootstrap(ROOT / "config" / "example.toml")
    try:
        kernel.start()
        print("HEALTH")
        print(json.dumps(kernel.health.report().to_dict(), indent=2))
        print("DIAGNOSTICS")
        print(json.dumps(collect_diagnostics().to_dict(), indent=2))
        return 0
    finally:
        kernel.stop()


if __name__ == "__main__":
    raise SystemExit(main())
