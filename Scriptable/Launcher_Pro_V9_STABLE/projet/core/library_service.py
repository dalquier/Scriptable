"""Façade métier coordonnant registre, imports, historique et exécution."""

from __future__ import annotations

import shutil
from pathlib import Path

from .history import HistoryEvent, HistoryJournal
from .importer import (
    ImporterError,
    detect_entry_point,
    discover_python_files,
    import_project,
    import_script,
    rename_imported_folder,
    suggest_entry_points,
)
from .logger import log
from .models import LauncherItem
from .registry import Registry
from .runner import RunResult, run_registered_item


class LibraryService:
    """API métier unique utilisée par le contrôleur de Launcher Pro."""

    def __init__(
        self,
        registry: Registry | None = None,
        history: HistoryJournal | None = None,
    ) -> None:
        self.registry = registry or Registry.load()
        self.history = history or HistoryJournal()

    def list_items(self, query: str = "", kind: str | None = None) -> list[LauncherItem]:
        """Recherche les éléments, favoris en premier."""
        return self.registry.search(query=query, kind=kind)

    def recent_history(self, limit: int = 100) -> list[HistoryEvent]:
        """Retourne les derniers événements métier."""
        return self.history.read(limit)

    def inspect_project(self, source_directory: str | Path) -> list[str]:
        """Retourne les points d'entrée possibles dans l'ordre recommandé."""
        files = discover_python_files(source_directory)
        if not files:
            raise ImporterError("Aucun fichier .py n'a été détecté dans ce dossier")
        return suggest_entry_points(files)

    def add_script(self, source_path: str | Path, display_name: str | None = None) -> LauncherItem:
        """Importe et enregistre un script, avec nettoyage transactionnel."""
        try:
            item = import_script(source_path, display_name)
            try:
                self.registry.add(item)
            except BaseException:
                self._remove_files(item)
                raise
        except BaseException as exc:
            self.history.append("import_script", success=False, detail=str(exc))
            raise
        self.history.append("import_script", item_id=item.id, detail=item.name)
        return item

    def add_project(
        self,
        source_directory: str | Path,
        entry_script: str | None = None,
        display_name: str | None = None,
    ) -> LauncherItem:
        """Importe un projet, en détectant l'entrée lorsqu'elle n'est pas fournie."""
        try:
            selected_entry = entry_script or detect_entry_point(source_directory)
            item = import_project(source_directory, selected_entry, display_name)
            try:
                self.registry.add(item)
            except BaseException:
                self._remove_files(item)
                raise
        except BaseException as exc:
            self.history.append("import_project", success=False, detail=str(exc))
            raise
        self.history.append("import_project", item_id=item.id, detail=item.name)
        return item

    def run(self, item_id: str) -> RunResult:
        """Exécute un élément et journalise son résultat."""
        result = run_registered_item(self.registry, item_id)
        self.history.append(
            "run", success=result.success, item_id=item_id,
            detail=result.target if result.success else (result.error or "Erreur inconnue"),
        )
        return result

    def rename(self, item_id: str, new_name: str) -> LauncherItem:
        """Renomme l'entrée et son dossier géré."""
        item = self.registry.require(item_id)
        old_name, old_path = item.name, item.local_path
        updated = rename_imported_folder(item, new_name)
        try:
            self.registry.update(updated)
        except BaseException:
            moved = Path(updated.local_path)
            moved_root = moved.parent if updated.kind == "script" else moved
            original = Path(old_path)
            original_root = original.parent if item.kind == "script" else original
            moved_root.rename(original_root)
            item.name, item.local_path = old_name, old_path
            raise
        self.history.append("rename", item_id=item_id, detail=f"{old_name} -> {updated.name}")
        return updated

    def set_favorite(self, item_id: str, favorite: bool) -> LauncherItem:
        """Modifie l'état favori d'un élément."""
        item = self.registry.require(item_id)
        item.favorite = bool(favorite)
        self.registry.update(item)
        self.history.append("favorite", item_id=item_id, detail=str(item.favorite))
        return item

    def delete(self, item_id: str, delete_files: bool = True) -> LauncherItem:
        """Supprime une entrée et, par défaut, sa copie locale gérée."""
        item = self.registry.require(item_id)
        removed = self.registry.remove(item_id)
        if delete_files:
            try:
                self._remove_files(item)
            except BaseException as exc:
                self.registry.add(item)
                self.history.append("delete", success=False, item_id=item_id, detail=str(exc))
                raise RuntimeError(f"Suppression des fichiers impossible : {exc}") from exc
        self.history.append("delete", item_id=item_id, detail=item.name)
        return removed

    @staticmethod
    def _remove_files(item: LauncherItem) -> None:
        local = Path(item.local_path)
        target = local.parent if item.kind == "script" else local
        if target.exists():
            log("LIBRARY", f"Suppression physique : {target}")
            shutil.rmtree(target)
