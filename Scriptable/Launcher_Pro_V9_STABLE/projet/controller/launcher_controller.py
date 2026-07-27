"""Contrôleur central traduisant des intentions en opérations métier."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from core.library_service import LibraryService


class Action(str, Enum):
    """Intentions supportées par le cœur au Sprint 1."""

    LIST = "list"
    IMPORT_SCRIPT = "import_script"
    INSPECT_PROJECT = "inspect_project"
    IMPORT_PROJECT = "import_project"
    RUN = "run"
    RENAME = "rename"
    DELETE = "delete"
    FAVORITE = "favorite"
    HISTORY = "history"


@dataclass(frozen=True)
class ControllerResult:
    """Réponse stable utilisable par une future UI Pyto."""

    success: bool
    value: Any = None
    error: str | None = None


class LauncherController:
    """Point d'entrée unique du cœur de Launcher Pro."""

    def __init__(self, service: LibraryService | None = None) -> None:
        self.service = service or LibraryService()

    def dispatch(self, action: Action | str, payload: Mapping[str, Any] | None = None) -> ControllerResult:
        """Exécute une intention et convertit toute erreur en résultat contrôlé."""
        data = dict(payload or {})
        try:
            selected = Action(action)
            handlers = {
                Action.LIST: lambda: self.service.list_items(data.get("query", ""), data.get("kind")),
                Action.IMPORT_SCRIPT: lambda: self.service.add_script(data["path"], data.get("name")),
                Action.INSPECT_PROJECT: lambda: self.service.inspect_project(data["path"]),
                Action.IMPORT_PROJECT: lambda: self.service.add_project(
                    data["path"], data.get("entry_script"), data.get("name")
                ),
                Action.RUN: lambda: self.service.run(data["id"]),
                Action.RENAME: lambda: self.service.rename(data["id"], data["name"]),
                Action.DELETE: lambda: self.service.delete(data["id"], data.get("delete_files", True)),
                Action.FAVORITE: lambda: self.service.set_favorite(data["id"], bool(data["favorite"])),
                Action.HISTORY: lambda: self.service.recent_history(int(data.get("limit", 100))),
            }
            return ControllerResult(True, handlers[selected]())
        except BaseException as exc:
            return ControllerResult(False, error=f"{type(exc).__name__}: {exc}")
