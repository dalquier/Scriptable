from __future__ import annotations

import ast
import shutil
from pathlib import Path
from typing import List, Optional

from .logger import log
from .models import LauncherItem
from .paths import PROJECTS_DIR, SCRIPTS_DIR, ensure_directories
from .registry import Registry


def validate_python_file(path: str | Path) -> Path:
    source = Path(path).expanduser().resolve()
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"Fichier introuvable : {source}")
    if source.suffix.lower() != ".py":
        raise ValueError("Le fichier sélectionné doit avoir l’extension .py")
    text = source.read_text(encoding="utf-8-sig", errors="strict")
    ast.parse(text, filename=str(source))
    return source


def validate_project(root: str | Path, entry_script: str) -> tuple[Path, Path]:
    project_root = Path(root).expanduser().resolve()
    if not project_root.exists() or not project_root.is_dir():
        raise NotADirectoryError(f"Dossier projet introuvable : {project_root}")
    entry = (project_root / entry_script).resolve()
    try:
        entry.relative_to(project_root)
    except ValueError as exc:
        raise ValueError("Le point d’entrée doit rester dans le dossier du projet") from exc
    validate_python_file(entry)
    return project_root, entry


def import_script(path: str | Path, name: Optional[str] = None, category: str = "Général", registry: Optional[Registry] = None) -> LauncherItem:
    ensure_directories()
    source = validate_python_file(path)
    active = registry or Registry.load()
    item = LauncherItem.create_script(name or source.stem, "", str(source))
    target = SCRIPTS_DIR / f"{item.id}_{source.name}"
    shutil.copy2(source, target)
    item.local_path = str(target)
    item.category = category.strip() or "Général"
    try:
        active.add(item)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    log(f"Script importé : {item.name}")
    return item


def add_project(root: str | Path, entry_script: str, name: Optional[str] = None, category: str = "Général", registry: Optional[Registry] = None) -> LauncherItem:
    ensure_directories()
    source_root, source_entry = validate_project(root, entry_script)
    active = registry or Registry.load()
    item = LauncherItem.create_project(name or source_root.name, "", str(source_entry.relative_to(source_root)))
    item.source_path = str(source_root)
    item.category = category.strip() or "Général"
    safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in source_root.name)
    target_root = PROJECTS_DIR / f"{item.id}_{safe_name or 'project'}"

    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored = {"__pycache__", ".git", ".DS_Store"}
        return {name for name in names if name in ignored or name.endswith(".pyc")}

    try:
        shutil.copytree(source_root, target_root, ignore=ignore)
        local_entry = target_root / item.entry_script
        validate_python_file(local_entry)
        item.project_root = str(target_root)
        active.add(item)
    except Exception:
        shutil.rmtree(target_root, ignore_errors=True)
        raise

    log(f"Projet importé : {item.name} ({item.entry_script})")
    return item


def list_python_files(directory: str | Path, recursive: bool = True) -> List[Path]:
    root = Path(directory).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"Dossier introuvable : {root}")
    pattern = "**/*.py" if recursive else "*.py"
    return sorted((path for path in root.glob(pattern) if path.is_file()), key=lambda path: (len(path.relative_to(root).parts), path.name.lower()))


def pick_file() -> str:
    try:
        import _sharing as sharing  # type: ignore
        picker = sharing.FilePicker()
        picker.allows_multiple_selection = False
        picker.file_extensions = []
        picker.mime_types = []
        picker.file_types = ["public.item"]
        sharing.pick_documents(picker)
        picked = sharing.picked_files()
        if not picked:
            raise RuntimeError("Aucun fichier sélectionné")
        return str(validate_python_file(picked[0]))
    except ImportError:
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
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"Dossier inaccessible : {root}")
    return str(root)
