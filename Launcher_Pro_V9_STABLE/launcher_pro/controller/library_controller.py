"""UI-agnostic orchestration for Launcher Pro."""

from pathlib import Path
from typing import List, Optional

from launcher_pro.registry import LibraryItem, LibraryRegistry, RegistryError
from launcher_pro.runner import PythonRunner, RunResult
from launcher_pro.services import ImportService


class LibraryController:
    def __init__(self, registry: LibraryRegistry, importer: ImportService = None, runner: PythonRunner = None):
        self.registry = registry
        self.importer = importer or ImportService()
        self.runner = runner or PythonRunner()

    def items(self, query: str = "", favorites_only: bool = False) -> List[LibraryItem]:
        needle = query.strip().casefold()
        matches = [
            item for item in self.registry.all()
            if (not favorites_only or item.favorite)
            and (not needle or needle in item.name.casefold() or needle in item.source_path.casefold())
        ]
        return sorted(matches, key=lambda item: (not item.favorite, item.name.casefold(), item.created_at))

    def import_script(self, path: str) -> LibraryItem:
        return self.registry.add(self.importer.script(Path(path)))

    def import_project(self, path: str) -> LibraryItem:
        return self.registry.add(self.importer.project(Path(path)))

    def rename(self, item_id: str, name: str) -> LibraryItem:
        return self.registry.rename(item_id, name)

    def toggle_favorite(self, item_id: str) -> LibraryItem:
        return self.registry.toggle_favorite(item_id)

    def delete(self, item_id: str) -> None:
        self.registry.remove(item_id)

    def run(self, item_id: str) -> RunResult:
        item = self.registry.find(item_id)
        if item is None:
            return RunResult(False, "Élément introuvable.")
        return self.runner.run(item)
