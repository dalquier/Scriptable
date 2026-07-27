"""Minimal DeveloperOS command-line interface."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from .core.bootstrap import bootstrap
from .core.diagnostics import collect_diagnostics
from .core.version import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(prog="developeros", description="DeveloperOS BUILD-1")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--config", help="Optional TOML configuration file")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("run", help="Start, report health, and stop the kernel")
    subparsers.add_parser("health", help="Print an aggregate health report")
    subparsers.add_parser("diagnostics", help="Print safe runtime diagnostics")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the DeveloperOS CLI and return a process exit code."""

    args = build_parser().parse_args(argv)
    if args.command == "diagnostics":
        print(json.dumps(collect_diagnostics().to_dict(), indent=2))
        return 0
    kernel = bootstrap(args.config)
    try:
        if args.command in {None, "run", "health"}:
            kernel.start()
            print(json.dumps(kernel.health.report().to_dict(), indent=2))
            return 0
        return 2
    finally:
        kernel.stop()


if __name__ == "__main__":
    raise SystemExit(main())
