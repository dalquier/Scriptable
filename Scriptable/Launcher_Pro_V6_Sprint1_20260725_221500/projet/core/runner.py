from __future__ import annotations

import contextlib
import io
import os
import runpy
import sys
import time
import traceback
from pathlib import Path

from .history import append_history
from .logger import log
from .models import RunnerResult, ScriptEntry, utc_now


def run_script(entry: ScriptEntry) -> RunnerResult:
    path = Path(entry.local_path)
    if not path.exists():
        result = RunnerResult(False, 0.0, error=f"Fichier local introuvable : {path}")
        _update_entry(entry, result)
        return result

    old_cwd = Path.cwd()
    old_argv = list(sys.argv)
    old_path = list(sys.path)
    output = io.StringIO()
    start = time.perf_counter()
    error = None

    try:
        os.chdir(path.parent)
        sys.argv = [str(path)]
        if str(path.parent) not in sys.path:
            sys.path.insert(0, str(path.parent))
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            runpy.run_path(str(path), run_name="__main__")
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
        os.chdir(old_cwd)
        sys.argv = old_argv
        sys.path[:] = old_path

    result = RunnerResult(success=success, duration=duration, error=error, output=output.getvalue())
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
        "error": result.error
    })
    level = "INFO" if result.success else "ERROR"
    log(f"Exécution {entry.name} : {entry.last_status} en {entry.last_duration}s", level)
