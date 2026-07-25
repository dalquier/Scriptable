from __future__ import annotations

import builtins
import io
import os
import sys
import time
import traceback
from pathlib import Path

from .logger import log
from .models import LauncherItem, RunnerResult, utc_now


class _Capture(io.StringIO):
    @property
    def buffer(self):
        return self

    def write(self, value):
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        return super().write(str(value))


def _resolve_target(item: LauncherItem) -> tuple[Path, Path]:
    if item.kind == "project":
        root = Path(item.project_root).expanduser().resolve()
        target = (root / item.entry_script).resolve()
        if not root.exists() or not root.is_dir():
            raise FileNotFoundError(f"Dossier projet introuvable : {root}")
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise ValueError("Le point d’entrée sort du dossier projet") from exc
        return root, target
    target = Path(item.local_path).expanduser().resolve()
    return target.parent, target


def run_item(item: LauncherItem) -> RunnerResult:
    start = time.perf_counter()
    output = _Capture()
    old_cwd = Path.cwd()
    old_argv = list(sys.argv)
    old_path = list(sys.path)
    old_stdout, old_stderr = sys.stdout, sys.stderr
    old_print = builtins.print
    success = False
    error = None

    try:
        workdir, target = _resolve_target(item)
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"Script d’entrée introuvable : {target}")
        code = compile(target.read_text(encoding="utf-8-sig"), str(target), "exec")
        os.chdir(workdir)
        sys.argv = [str(target)]
        if str(workdir) not in sys.path:
            sys.path.insert(0, str(workdir))
        if str(target.parent) not in sys.path:
            sys.path.insert(0, str(target.parent))
        sys.stdout = output
        sys.stderr = output

        def captured_print(*args, **kwargs):
            kwargs = dict(kwargs)
            kwargs["file"] = output
            old_print(*args, **kwargs)

        builtins.print = captured_print
        globals_dict = {
            "__name__": "__main__",
            "__file__": str(target),
            "__package__": None,
            "__cached__": None,
            "__builtins__": builtins.__dict__,
        }
        exec(code, globals_dict, globals_dict)
        success = True
    except SystemExit as exc:
        success = exc.code in (None, 0)
        if not success:
            error = f"SystemExit: {exc.code}"
    except BaseException:
        error = traceback.format_exc()
    finally:
        duration = time.perf_counter() - start
        builtins.print = old_print
        sys.stdout, sys.stderr = old_stdout, old_stderr
        os.chdir(old_cwd)
        sys.argv = old_argv
        sys.path[:] = old_path

    result = RunnerResult(success=success, duration=duration, output=output.getvalue(), error=error)
    item.run_count += 1
    item.last_run_at = utc_now()
    item.last_duration = round(duration, 4)
    item.last_status = "success" if success else "error"
    item.last_error = error
    log(f"Exécution {item.kind} {item.name} : {item.last_status} en {item.last_duration}s", "INFO" if success else "ERROR")
    return result
