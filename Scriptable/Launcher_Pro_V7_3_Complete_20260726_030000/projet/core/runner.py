from __future__ import annotations

import builtins
import contextlib
import io
import os
import sys
import time
import traceback
from pathlib import Path

from .models import LauncherItem, RunnerResult, utc_now


class _PrintCapture(io.TextIOBase):
    def __init__(self) -> None:
        self.buffer = io.StringIO()

    def write(self, value: str) -> int:
        return self.buffer.write(str(value))

    def flush(self) -> None:
        return None

    def getvalue(self) -> str:
        return self.buffer.getvalue()


def _resolve_target(item: LauncherItem) -> tuple[Path, Path]:
    if item.kind == "project":
        root = Path(item.project_root).expanduser().resolve()
        target = (root / item.entry_script).resolve()
    else:
        target = Path(item.local_path).expanduser().resolve()
        root = target.parent
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Dossier introuvable : {root}")
    if not target.exists() or not target.is_file():
        raise FileNotFoundError(f"Script introuvable : {target}")
    return root, target


def run_item(item: LauncherItem) -> RunnerResult:
    started = time.perf_counter()
    capture = _PrintCapture()
    previous_cwd = Path.cwd()
    previous_argv = list(sys.argv)
    previous_path = list(sys.path)
    previous_stdout = sys.stdout
    previous_stderr = sys.stderr
    original_print = builtins.print

    try:
        root, target = _resolve_target(item)
        os.chdir(root)
        sys.argv = [str(target)]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))

        def captured_print(*args, **kwargs):
            kwargs = dict(kwargs)
            kwargs["file"] = capture
            original_print(*args, **kwargs)

        builtins.print = captured_print
        sys.stdout = capture
        sys.stderr = capture

        source = target.read_text(encoding="utf-8-sig")
        code = compile(source, str(target), "exec")
        globals_dict = {
            "__name__": "__main__",
            "__file__": str(target),
            "__package__": None,
            "__cached__": None,
        }
        with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
            exec(code, globals_dict, globals_dict)

        duration = time.perf_counter() - started
        result = RunnerResult(True, duration, capture.getvalue(), None)
        item.last_status = "success"
        item.last_error = None
    except BaseException:
        duration = time.perf_counter() - started
        error = traceback.format_exc()
        result = RunnerResult(False, duration, capture.getvalue(), error)
        item.last_status = "error"
        item.last_error = error
    finally:
        builtins.print = original_print
        sys.stdout = previous_stdout
        sys.stderr = previous_stderr
        sys.argv = previous_argv
        sys.path[:] = previous_path
        os.chdir(previous_cwd)

    item.last_run_at = utc_now()
    item.last_duration = result.duration
    item.run_count += 1
    return result
