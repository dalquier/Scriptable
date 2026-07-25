from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import quote

from .registry import Registry
from .runner import run_item


def launcher_script_path() -> Path:
    return Path(__file__).resolve().parent.parent / "LauncherPro.py"


def url_entry_path() -> Path:
    return Path(__file__).resolve().parent.parent / "LauncherProURL.py"


def build_open_url() -> str:
    code = (
        "import runpy;"
        f"runpy.run_path({str(launcher_script_path())!r}, run_name='__main__')"
    )
    return "pyto://x-callback/?code=" + quote(code, safe="")


def build_run_url(item_id: str) -> str:
    code = (
        "import runpy,sys;"
        f"sys.argv=[{str(url_entry_path())!r},{item_id!r}];"
        f"runpy.run_path({str(url_entry_path())!r}, run_name='__main__')"
    )
    return "pyto://x-callback/?code=" + quote(code, safe="")


def run_by_id(item_id: str):
    registry = Registry.load()
    item = registry.require(item_id)
    result = run_item(item)
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
