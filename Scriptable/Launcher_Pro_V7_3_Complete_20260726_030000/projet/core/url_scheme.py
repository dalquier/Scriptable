from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import quote

from .history import append_history
from .registry import Registry
from .runner import run_item


def launcher_script_path() -> Path:
    return Path(__file__).resolve().parent.parent / "LauncherPro.py"


def url_entry_path() -> Path:
    return Path(__file__).resolve().parent.parent / "LauncherProURL.py"


def _bootstrap_code(path: Path, argv: list[str]) -> str:
    root = path.parent
    return (
        "import os,runpy,sys;"
        f"p={str(path)!r};r={str(root)!r};"
        "sys.path.insert(0,r) if r not in sys.path else None;"
        "os.chdir(r);"
        f"sys.argv={argv!r};"
        "runpy.run_path(p,run_name='__main__')"
    )


def build_open_url() -> str:
    path = launcher_script_path()
    code = _bootstrap_code(path, [str(path)])
    return "pyto://x-callback/?code=" + quote(code, safe="")


def build_run_url(item_id: str) -> str:
    path = url_entry_path()
    code = _bootstrap_code(path, [str(path), item_id])
    return "pyto://x-callback/?code=" + quote(code, safe="")


def run_by_id(item_id: str):
    registry = Registry.load()
    item = registry.require(item_id)
    result = run_item(item)
    append_history(item, result)
    registry.update(item)
    return item, result


def copy_text(text: str) -> bool:
    try:
        import pasteboard  # type: ignore
        setter = getattr(pasteboard, "set_string", None)
        if callable(setter):
            setter(text)
            return True
    except Exception:
        pass
    try:
        import clipboard  # type: ignore
        setter = getattr(clipboard, "set", None)
        if callable(setter):
            setter(text)
            return True
    except Exception:
        pass
    return False


def item_id_from_argv() -> str | None:
    args = list(sys.argv[1:])
    if not args:
        return None
    if args[0] == "--run" and len(args) > 1:
        return args[1]
    return args[0]
