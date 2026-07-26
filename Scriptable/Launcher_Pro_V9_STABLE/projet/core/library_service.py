"""Services métier de Launcher Pro.

Cette couche coordonne l'importeur, le registre et le moteur d'exécution.
L'interface utilisateur n'accède jamais directement aux fichiers techniques.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from core.importer import (
    ImporterError,
    discover_python_files,
    import_project,
    import_script,
    rename_imported_folder,
    suggest_entry_points,
)
from core.logger import log
from core.models import LauncherItem
from core.registry import Registry
from core.runner import RunResult, run_registered_item


class LibraryService:
    """Façade unique pour gérer et exécuter la bibliothèque Launcher Pro."""

    def __init__(self, registry: Registry | None = None) -> None:
        self.registry = registry or Registry.load()

    def list_items(self, query: str = "", kind: str | None = None) -> list[LauncherItem]:
        return self.registry.search(query=query, kind=kind)

    def inspect_project(self, source_directory: str | Path) -> list[str]:
        """Retourne les points d'entrée possibles dans l'ordre recommandé."""
        files = discover_python_files(source_directory)
        if not files:
            raise ImporterError("Aucun fichier .py n'a été détecté dans ce dossier")
        suggestions = suggest_entry_points(files)
        log("LIBRARY", f"Points d'entrée proposés : {suggestions}")
        return suggestions

    def add_script(self, source_path: str | Path, display_name: str | None = None) -> LauncherItem:
        log("LIBRARY", f"Demande d'ajout de script : {source_path}")
        item = import_script(source_path, display_name)
        try:
            self.registry.add(item)
        except Exception:
            self._remove_files(item)
            raise
        return item

    def add_project(
        self,
        source_directory: str | Path,
        entry_script: str,
        display_name: str | None = None,
    ) -> LauncherItem:
        log("LIBRARY", f"Demande d'ajout de projet : {source_directory}")
        item = import_project(source_directory, entry_script, display_name)
        try:
            self.registry.add(item)
        except Exception:
            self._remove_files(item)
            raise
        return item

    def run(self, item_id: str) -> RunResult:
        """Lance un élément après fermeture de l'interface appelante."""
        log("LIBRARY", f"Demande de lancement : {item_id}")
        return run_registered_item(self.registry, item_id)

    def rename(self, item_id: str, new_name: str) -> LauncherItem:
        item = self.registry.require(item_id)
        updated = rename_imported_folder(item, new_name)
        try:
            self.registry.update(updated)
        except Exception:
            log(
                "LIBRARY",
                "Le dossier a été renommé mais la mise à jour du registre a échoué",
                force=True,
            )
            raise
        return updated

    def set_favorite(self, item_id: str, favorite: bool) -> LauncherItem:
        item = self.registry.require(item_id)
        item.favorite = bool(favorite)
        self.registry.update(item)
        log("LIBRARY", f"Favori {item.name} = {item.favorite}")
        return item

    def delete(self, item_id: str, delete_files: bool = True) -> LauncherItem:
        item = self.registry.require(item_id)
        removed = self.registry.remove(item_id)
        if delete_files:
            try:
                self._remove_files(item)
            except Exception as exc:
                self.registry.add(item)
                raise RuntimeError(f"Suppression des fichiers impossible : {exc}") from exc
        log("LIBRARY", f"Élément supprimé : {item.name}")
        return removed

    @staticmethod
    def _remove_files(item: LauncherItem) -> None:
        local = Path(item.local_path)
        target = local.parent if item.kind == "script" else local
        if not target.exists():
            log("LIBRARY", f"Fichiers déjà absents : {target}", force=True)
            return
        log("LIBRARY", f"Suppression physique : {target}")
        shutil.rmtree(target)
