"""Moteur d'exécution isolé de Launcher Pro V9.

Le lanceur exécute le fichier cible dans le processus Python courant, mais restaure
ensuite le dossier de travail, ``sys.path``, ``sys.argv`` et le module ``__main__``.
Cette stratégie limite les effets de bord entre deux lancements successifs.
"""

from __future__ import annotations

import os
import runpy
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType

from .logger import log, log_exception
from .models import LauncherItem
from .registry import Registry


class RunnerError(RuntimeError):
    """Erreur de préparation ou d'exécution présentable à l'utilisateur."""


@dataclass(frozen=True)
class RunResult:
    """Résultat complet d'un lancement."""

    item_id: str
    success: bool
    duration: float
    target: str
    error: str | None = None
    traceback_text: str | None = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_target(item: LauncherItem) -> tuple[Path, Path]:
    """Retourne ``(fichier à exécuter, dossier de travail)``."""

    item.validate()

    if item.kind == "script":
        target = Path(item.local_path).expanduser().resolve()
        working_directory = target.parent
    else:
        project_directory = Path(item.local_path).expanduser().resolve()
        target = (project_directory / item.entry_script).resolve()
        working_directory = project_directory

        try:
            target.relative_to(project_directory)
        except ValueError as exc:
            raise RunnerError("Le point d'entrée sort du dossier du projet") from exc

    if not target.exists():
        raise RunnerError(f"Fichier de lancement introuvable : {target}")
    if not target.is_file():
        raise RunnerError(f"La cible n'est pas un fichier : {target}")
    if target.suffix.lower() != ".py":
        raise RunnerError("La cible de lancement doit être un fichier .py")

    return target, working_directory


def execute_item(item: LauncherItem) -> RunResult:
    """Exécute un élément et restaure systématiquement l'environnement global."""

    target, working_directory = resolve_target(item)
    started = time.perf_counter()

    old_cwd = Path.cwd()
    old_sys_path = list(sys.path)
    old_argv = list(sys.argv)
    old_main: ModuleType | None = sys.modules.get("__main__")

    log("RUNNER", f"Préparation : {item.kind} · {item.name}")
    log("RUNNER", f"Cible : {target}")
    log("RUNNER", f"Dossier de travail : {working_directory}")

    try:
        os.chdir(working_directory)
        sys.path.insert(0, str(working_directory))
        sys.argv = [str(target)]

        log("RUNNER", "Exécution démarrée")
        runpy.run_path(str(target), run_name="__main__")

        duration = time.perf_counter() - started
        log("RUNNER", f"Exécution terminée avec succès en {duration:.3f} s")
        return RunResult(
            item_id=item.id,
            success=True,
            duration=duration,
            target=str(target),
        )

    except SystemExit as exc:
        duration = time.perf_counter() - started
        code = exc.code
        if code in (None, 0):
            log("RUNNER", f"SystemExit normal en {duration:.3f} s")
            return RunResult(item.id, True, duration, str(target))

        message = f"Le script s'est arrêté avec le code {code}"
        log("RUNNER", message, force=True)
        return RunResult(item.id, False, duration, str(target), message)

    except BaseException as exc:
        duration = time.perf_counter() - started
        trace = traceback.format_exc()
        log_exception("RUNNER", exc)
        log("RUNNER", trace.rstrip(), force=True)
        return RunResult(
            item_id=item.id,
            success=False,
            duration=duration,
            target=str(target),
            error=f"{type(exc).__name__}: {exc}",
            traceback_text=trace,
        )

    finally:
        os.chdir(old_cwd)
        sys.path[:] = old_sys_path
        sys.argv[:] = old_argv

        if old_main is not None:
            sys.modules["__main__"] = old_main
        else:
            sys.modules.pop("__main__", None)

        log("RUNNER", "Environnement Python restauré")


def run_registered_item(registry: Registry, item_id: str) -> RunResult:
    """Lance un élément du registre puis enregistre son résultat."""

    item = registry.require(item_id)
    log("RUNNER", f"Lancement demandé pour l'identifiant {item_id}")

    try:
        result = execute_item(item)
    except BaseException as exc:
        # Les erreurs de préparation doivent également être persistées.
        log_exception("RUNNER", exc)
        result = RunResult(
            item_id=item.id,
            success=False,
            duration=0.0,
            target=item.local_path,
            error=f"{type(exc).__name__}: {exc}",
            traceback_text=traceback.format_exc(),
        )

    item.run_count += 1
    item.last_run_at = _utc_now()
    item.last_duration = round(result.duration, 6)
    item.last_status = "success" if result.success else "error"
    item.last_error = None if result.success else result.error
    registry.update(item)

    log(
        "RUNNER",
        f"Résultat enregistré : statut={item.last_status}, lancements={item.run_count}",
        force=not result.success,
    )
    return result
