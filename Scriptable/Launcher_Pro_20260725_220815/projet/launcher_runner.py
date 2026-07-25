from __future__ import annotations

from datetime import datetime
import os
import runpy
import sys
import traceback


def run_entry(entry) -> tuple[bool, str]:
    path = os.path.abspath(entry.local_path)
    if not os.path.isfile(path):
        return False, f"Fichier introuvable : {path}"

    previous_cwd = os.getcwd()
    previous_argv = list(sys.argv)
    script_dir = os.path.dirname(path)
    added_to_path = False

    try:
        os.chdir(script_dir)
        sys.argv = [path]
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
            added_to_path = True
        runpy.run_path(path, run_name="__main__")
        entry.last_run_at = datetime.now().isoformat(timespec="seconds")
        entry.run_count += 1
        entry.last_status = "success"
        entry.last_error = ""
        return True, "Exécution terminée"
    except SystemExit as exc:
        code = exc.code
        ok = code in (None, 0)
        entry.last_run_at = datetime.now().isoformat(timespec="seconds")
        entry.run_count += 1
        entry.last_status = "success" if ok else "error"
        entry.last_error = "" if ok else f"SystemExit({code})"
        return ok, "Script terminé" if ok else entry.last_error
    except BaseException:
        message = traceback.format_exc()
        entry.last_run_at = datetime.now().isoformat(timespec="seconds")
        entry.run_count += 1
        entry.last_status = "error"
        entry.last_error = message[-4000:]
        return False, message
    finally:
        os.chdir(previous_cwd)
        sys.argv = previous_argv
        if added_to_path:
            try:
                sys.path.remove(script_dir)
            except ValueError:
                pass
