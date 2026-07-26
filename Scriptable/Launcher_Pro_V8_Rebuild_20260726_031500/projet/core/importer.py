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
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"Fichier introuvable : {source}")
    if source.suffix.lower() != ".py":
        raise ValueError("Le fichier sélectionné doit avoir l’extension .py")
    ast.parse(source.read_text(encoding="utf-8-sig"), filename=str(source))
    return source


def list_python_files(directory: str | Path) -> list[Path]:
    root = Path(directory).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"Dossier introuvable : {root}")
    return sorted(
        (p for p in root.rglob("*.py") if p.is_file()),
        key=lambda p: (len(p.relative_to(root).parts), str(p.relative_to(root)).lower()),
    )


def import_script(path: str | Path, name: Optional[str] = None, registry: Optional[Registry] = None) -> LauncherItem:
    ensure_directories()
    source = validate_python_file(path)
    active = registry or Registry.load()
    item = LauncherItem.create_script(name or source.stem, "", str(source))
    target = SCRIPTS_DIR / f"{item.id}_{source.name}"
    shutil.copy2(source, target)
    item.local_path = str(target)
    try:
        active.add(item)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return item


def add_project(root: str | Path, entry_script: str, name: Optional[str] = None, registry: Optional[Registry] = None) -> LauncherItem:
    ensure_directories()
    source_root = Path(root).expanduser().resolve()
    if not source_root.exists() or not source_root.is_dir():
        raise NotADirectoryError(f"Dossier projet introuvable : {source_root}")
    source_entry = validate_python_file(source_root / entry_script)
    try:
        source_entry.relative_to(source_root)
    except ValueError as exc:
        raise ValueError("Le fichier de lancement doit être dans le projet") from exc
    active = registry or Registry.load()
    item = LauncherItem.create_project(name or source_root.name, "", str(source_entry.relative_to(source_root)))
    item.source_path = str(source_root)
    safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in source_root.name)
    target_root = PROJECTS_DIR / f"{item.id}_{safe_name or 'project'}"

    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in {"__pycache__", ".git", ".DS_Store"} or name.endswith(".pyc")}

    try:
        shutil.copytree(source_root, target_root, ignore=ignore)
        validate_python_file(target_root / item.entry_script)
        item.project_root = str(target_root)
        active.add(item)
    except Exception:
        shutil.rmtree(target_root, ignore_errors=True)
        raise
    return item


def _one_path(result) -> str:
    if isinstance(result, (list, tuple)):
        result = result[0] if result else None
    if not result:
        raise RuntimeError("Sélection annulée")
    return str(result)


def pick_file() -> str:
    """Utilise le sélecteur officiel Pyto, hors de toute vue modale."""
    import file_system  # type: ignore

    try:
        result = file_system.import_file(multiple_selection=False)
    except TypeError:
        result = file_system.import_file()
    return str(validate_python_file(_one_path(result)))


def pick_directory() -> str:
    import file_system  # type: ignore

    root = Path(_one_path(file_system.pick_directory())).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"Dossier inaccessible : {root}")
    return str(root)
