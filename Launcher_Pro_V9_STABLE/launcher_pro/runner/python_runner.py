"""Safe process-state wrapper around Python script execution."""

import os
import runpy
import sys
import traceback
from threading import Lock
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from launcher_pro.registry import ItemKind, LibraryItem


@dataclass(frozen=True)
class RunResult:
    succeeded: bool
    error: Optional[str] = None


class PythonRunner:
    """Run one item at a time and always restore global interpreter state."""

    _execution_lock = Lock()

    def run(self, item: LibraryItem) -> RunResult:
        if not self._execution_lock.acquire(blocking=False):
            return RunResult(False, "Une autre exécution est déjà en cours.")
        try:
            return self._run_locked(item)
        finally:
            self._execution_lock.release()

    def _run_locked(self, item: LibraryItem) -> RunResult:
        entrypoint = Path(item.entrypoint)
        if not entrypoint.is_file():
            return RunResult(False, "Point d'entrée introuvable : {}".format(entrypoint))
        working_directory = Path(item.source_path) if item.kind == ItemKind.PROJECT else entrypoint.parent
        previous_cwd, previous_argv, previous_path = Path.cwd(), sys.argv[:], sys.path[:]
        try:
            os.chdir(str(working_directory))
            sys.argv = [str(entrypoint)]
            sys.path.insert(0, str(working_directory))
            runpy.run_path(str(entrypoint), run_name="__main__")
            return RunResult(True)
        except SystemExit as exc:
            if exc.code in (None, 0):
                return RunResult(True)
            return RunResult(False, "Le script s'est arrêté avec le code {}.".format(exc.code))
        except BaseException:
            return RunResult(False, traceback.format_exc())
        finally:
            os.chdir(str(previous_cwd))
            sys.argv = previous_argv
            sys.path[:] = previous_path
