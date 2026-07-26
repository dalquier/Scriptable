from __future__ import annotations

import ast
import shutil
from pathlib import Path
from typing import Optional

from .models import LauncherItem
from .paths import PROJECTS_DIR, SCRIPTS_DIR, ensure_directories
from .registry import Registry


def validate_python_file(path: str | Path) -> Path:
    source = Path(path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Fichier introuvable : {source}")
    if source.suffix.lower() != ".py":
        raise ValueError("Le fichier sélectionné doit avoir l’extension .py")
    ast.parse(source.read_text(encoding="utf-8-sig"), filename=str(source))
    return source


def list_python_files(directory: str | Path) -> list[Path]:
    root = Path(directory).expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Dossier introuvable : {root}")
    return sorted((p for p in root.rglob("*.py") if p.is_file()), key=lambda p: (len(p.relative_to(root).parts), str(p.relative_to(root)).lower()))


def import_script(path: str | Path, name: Optional[str] = None, registry: Optional[Registry] = None) -> LauncherItem:
    ensure_directories()
    source = validate_python_file(path)
    active = registry or Registry.load()
    item = LauncherItem.create_script(name or source.stem, "", str(source))
    target = SCRIPTS_DIR / f"{item.id}_{source.name}"
    shutil.copy2(source, target)
    item.local_path = str(target)
    active.add(item)
    return item


def add_project(root: str | Path, entry_script: str, name: Optional[str] = None, registry: Optional[Registry] = None) -> LauncherItem:
    ensure_directories()
    source_root = Path(root).expanduser().resolve()
    if not source_root.is_dir():
        raise NotADirectoryError(f"Dossier projet introuvable : {source_root}")
    source_entry = validate_python_file(source_root / entry_script)
    source_entry.relative_to(source_root)
    active = registry or Registry.load()
    item = LauncherItem.create_project(name or source_root.name, "", str(source_entry.relative_to(source_root)))
    item.source_path = str(source_root)
    safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in source_root.name)
    target_root = PROJECTS_DIR / f"{item.id}_{safe_name or 'project'}"

    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in {"__pycache__", ".git", ".DS_Store"} or name.endswith(".pyc")}

    shutil.copytree(source_root, target_root, ignore=ignore)
    validate_python_file(target_root / item.entry_script)
    item.project_root = str(target_root)
    active.add(item)
    return item


def pick_file() -> str:
    import file_system  # type: ignore
    result = file_system.import_file(multiple_selection=False)
    if isinstance(result, (list, tuple)):
        result = result[0] if result else None
    if not result:
        raise RuntimeError("Aucun fichier sélectionné")
    return str(validate_python_file(result))


def pick_directory() -> str:
    import file_system  # type: ignore
    result = file_system.pick_directory()
    if not result:
        raise RuntimeError("Aucun dossier sélectionné")
    root = Path(result).expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Dossier inaccessible : {root}")
    return str(root)
