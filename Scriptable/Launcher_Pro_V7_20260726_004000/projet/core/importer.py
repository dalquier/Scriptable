from __future__ import annotations

import ast
import shutil
from pathlib import Path
from typing import List, Optional

from .logger import log
from .models import LauncherItem
from .paths import SCRIPTS_DIR, ensure_directories
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
    provisional = LauncherItem.create_script(name or source.stem, "", str(source))
    target = SCRIPTS_DIR / f"{provisional.id}_{source.name}"
    shutil.copy2(source, target)
    provisional.local_path = str(target)
    provisional.category = category.strip() or "Général"
    try:
        active.add(provisional)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    log(f"Script importé : {provisional.name}")
    return provisional


def add_project(root: str | Path, entry_script: str, name: Optional[str] = None, category: str = "Général", registry: Optional[Registry] = None) -> LauncherItem:
    project_root, entry = validate_project(root, entry_script)
    active = registry or Registry.load()
    item = LauncherItem.create_project(name or project_root.name, str(project_root), str(entry.relative_to(project_root)))
    item.category = category.strip() or "Général"
    active.add(item)
    log(f"Projet ajouté : {item.name} ({item.entry_script})")
    return item


def list_python_files(directory: str | Path, recursive: bool = True) -> List[Path]:
    root = Path(directory).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"Dossier introuvable : {root}")
    pattern = "**/*.py" if recursive else "*.py"
    return sorted((path for path in root.glob(pattern) if path.is_file()), key=lambda path: (len(path.parts), path.name.lower()))


def pick_file() -> str:
    import file_system  # type: ignore
    result = file_system.import_file(multiple_selection=False, type_identifier="public.item")
    if isinstance(result, (list, tuple)):
        result = result[0] if result else None
    if not result:
        raise RuntimeError("Aucun fichier sélectionné")
    return str(result)


def pick_directory() -> str:
    import file_system  # type: ignore
    result = file_system.pick_directory()
    if not result:
        raise RuntimeError("Aucun dossier sélectionné")
    return str(result)
