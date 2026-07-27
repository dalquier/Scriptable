"""Import user-selected sources into optional managed application storage."""

import shutil
from pathlib import Path
from typing import Optional
from uuid import uuid4

from launcher_pro.registry import ItemKind, LibraryItem
from .entrypoints import EntrypointDetector


class ImportService:
    """Validate imports and, when configured, keep durable private copies."""

    def __init__(self, detector: EntrypointDetector = None, storage_root: Optional[Path] = None):
        self.detector = detector or EntrypointDetector()
        self.storage_root = Path(storage_root) if storage_root is not None else None

    def script(self, path: Path) -> LibraryItem:
        source = self.detector.detect_script(path)
        imported = self._copy_script(source) if self.storage_root else source
        return LibraryItem.create(source.stem, ItemKind.SCRIPT, imported, imported)

    def project(self, path: Path) -> LibraryItem:
        source_root = Path(path).expanduser().resolve()
        source_entrypoint = self.detector.detect_project(source_root)
        if self.storage_root:
            imported_root = self._copy_project(source_root)
            relative_entrypoint = source_entrypoint.relative_to(source_root)
            imported_entrypoint = imported_root / relative_entrypoint
        else:
            imported_root, imported_entrypoint = source_root, source_entrypoint
        return LibraryItem.create(source_root.name, ItemKind.PROJECT, imported_root, imported_entrypoint)

    def _copy_script(self, source: Path) -> Path:
        destination_dir = self._new_destination("scripts", source.stem)
        try:
            destination_dir.mkdir(parents=True)
            destination = destination_dir / source.name
            shutil.copy2(str(source), str(destination))
            return destination.resolve()
        except Exception:
            shutil.rmtree(str(destination_dir), ignore_errors=True)
            raise

    def _copy_project(self, source: Path) -> Path:
        destination = self._new_destination("projects", source.name)
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(str(source), str(destination), ignore=self._ignored_files)
            return destination.resolve()
        except Exception:
            shutil.rmtree(str(destination), ignore_errors=True)
            raise

    def _new_destination(self, category: str, name: str) -> Path:
        safe_name = "".join(character if character.isalnum() or character in "-_" else "_" for character in name)
        return self.storage_root / category / "{}_{}".format(uuid4().hex, safe_name or category[:-1])

    @staticmethod
    def _ignored_files(_directory: str, names):
        return {name for name in names if name in {".git", ".venv", "venv", "__pycache__", ".DS_Store"}
                or name.endswith((".pyc", ".pyo"))}
