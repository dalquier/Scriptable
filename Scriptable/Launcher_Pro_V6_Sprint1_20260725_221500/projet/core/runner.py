from __future__ import annotations

import builtins
import io
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict

from .history import append_history
from .logger import log
from .models import RunnerResult, ScriptEntry, utc_now


class _CaptureStream(io.StringIO):
    """Flux texte compatible avec les usages courants de stdout/stderr."""

    encoding = "utf-8"

    def isatty(self) -> bool:
        return False

    def flush(self) -> None:
        return None



def _build_builtins(output: _CaptureStream) -> Dict[str, Any]:
    """Crée un espace builtins dont print est capturé de façon fiable dans Pyto."""
    namespace = dict(vars(builtins))
    original_print = builtins.print

    def captured_print(*args, **kwargs):
        requested_file = kwargs.get("file")
        if requested_file is None or requested_file in (sys.stdout, sys.stderr):
            kwargs = dict(kwargs)
            kwargs["file"] = output
            original_print(*args, **kwargs)
        else:
            original_print(*args, **kwargs)

    namespace["print"] = captured_print
    return namespace



def run_script(entry: ScriptEntry) -> RunnerResult:
    path = Path(entry.local_path)
    if not path.exists():
        result = RunnerResult(False, 0.0, error=f"Fichier local introuvable : {path}")
        _update_entry(entry, result)
        return result

    old_cwd = Path.cwd()
    old_argv = list(sys.argv)
    old_path = list(sys.path)
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    output = _CaptureStream()
    start = time.perf_counter()
    error = None
    success = False

    try:
        os.chdir(path.parent)
        sys.argv = [str(path)]
        if str(path.parent) not in sys.path:
            sys.path.insert(0, str(path.parent))

        source = path.read_text(encoding="utf-8-sig")
        code = compile(source, str(path), "exec")
        globals_dict = {
            "__name__": "__main__",
            "__file__": str(path),
            "__package__": None,
            "__cached__": None,
            "__builtins__": _build_builtins(output),
        }

        sys.stdout = output
        sys.stderr = output
        exec(code, globals_dict, globals_dict)
        success = True
    except SystemExit as exc:
        success = exc.code in (None, 0)
        if not success:
            error = f"SystemExit: {exc.code}"
    except BaseException:
        success = False
        error = traceback.format_exc()
    finally:
        duration = time.perf_counter() - start
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        os.chdir(old_cwd)
        sys.argv = old_argv
        sys.path[:] = old_path

    result = RunnerResult(
        success=success,
        duration=duration,
        error=error,
        output=output.getvalue(),
    )
    _update_entry(entry, result)
    return result



def _update_entry(entry: ScriptEntry, result: RunnerResult) -> None:
    entry.run_count += 1
    entry.last_run_at = utc_now()
    entry.last_duration = round(result.duration, 4)
    entry.last_status = "success" if result.success else "error"
    entry.last_error = result.error
    append_history({
        "date": entry.last_run_at,
        "script_id": entry.id,
        "script_name": entry.name,
        "duration": entry.last_duration,
        "status": entry.last_status,
        "error": result.error,
        "output": result.output[-2000:],
    })
    level = "INFO" if result.success else "ERROR"
    log(f"Exécution {entry.name} : {entry.last_status} en {entry.last_duration}s", level)
