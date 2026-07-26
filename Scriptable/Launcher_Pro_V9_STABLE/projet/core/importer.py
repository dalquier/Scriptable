"""Import sécurisé des scripts et projets dans la bibliothèque Launcher Pro.

Ce module ne dépend pas de pyto_ui. Il reçoit des chemins déjà choisis par
l'utilisateur, valide les sources, copie les fichiers puis renvoie un objet
LauncherItem prêt à être ajouté au registre.
"""

from __future__ import annotations

import ast
import shutil
from dataclasses import replace
from pathlib import Path
from typing import Iterable

from core.logger import log
from core.models import LauncherItem
from core.paths import PROJECTS_DIR, SCRIPTS_DIR, ensure_directories


class ImporterError(RuntimeError):
    """Erreur d'import compréhensible par l'interface."""


def _safe_folder_name(value: str) -> str:
    """Transforme un libellé en nom de dossier simple et prévisible."""
    cleaned = "".join(
        char if char.isalnum() or char in {"-", "_"} else "_"
        for char in value.strip()
    )
    cleaned = cleaned.strip("._-")
    return cleaned or "element"


def _unique_destination(parent: Path, requested_name: str) -> Path:
    """Retourne un chemin libre sans écraser un import précédent."""
    base = _safe_folder_name(requested_name)
    candidate = parent / base
    index = 2
    while candidate.exists():
        candidate = parent / f"{base}_{index}"
        index += 1
    return candidate


def validate_python_file(path: str | Path) -> Path:
    """Vérifie extension, existence, lisibilité et syntaxe d'un fichier Python."""
    source = Path(path).expanduser().resolve()
    log("IMPORT", f"Validation du fichier Python : {source}")

    if not source.exists():
        raise ImporterError(f"Fichier introuvable : {source}")
    if not source.is_file():
        raise ImporterError(f"Le chemin sélectionné n'est pas un fichier : {source}")
    if source.suffix.lower() != ".py":
        raise ImporterError("Le fichier sélectionné doit porter l'extension .py")

    try:
        text = source.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ImporterError("Le fichier Python doit être encodé en UTF-8") from exc
    except OSError as exc:
        raise ImporterError(f"Impossible de lire le fichier : {exc}") from exc

    try:
        ast.parse(text, filename=str(source))
    except SyntaxError as exc:
        line = exc.lineno or "?"
        raise ImporterError(
            f"Erreur de syntaxe dans {source.name}, ligne {line} : {exc.msg}"
        ) from exc

    log("IMPORT", "Validation syntaxique terminée avec succès")
    return source


def discover_python_files(project_directory: str | Path) -> list[str]:
    """Liste les fichiers .py d'un projet sous forme de chemins relatifs."""
    root = Path(project_directory).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ImporterError(f"Dossier projet introuvable : {root}")

    ignored = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".venv", "venv"}
    results: list[str] = []

    for path in root.rglob("*.py"):
        if any(part in ignored for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            results.append(path.relative_to(root).as_posix())

    results.sort(key=lambda value: (value.count("/"), value.casefold()))
    log("IMPORT", f"{len(results)} fichier(s) Python détecté(s) dans {root.name}")
    return results


def suggest_entry_points(files: Iterable[str]) -> list[str]:
    """Classe les points d'entrée probables avant les autres fichiers."""
    candidates = list(files)
    priorities = {
        "main.py": 0,
        "app.py": 1,
        "launcher.py": 2,
        "run.py": 3,
        "start.py": 4,
        "__main__.py": 5,
    }
    return sorted(
        candidates,
        key=lambda value: (
            priorities.get(Path(value).name.casefold(), 100),
            value.count("/"),
            value.casefold(),
        ),
    )


def import_script(source_path: str | Path, display_name: str | None = None) -> LauncherItem:
    """Copie un script dans library/scripts et construit son entrée de registre."""
    ensure_directories()
    source = validate_python_file(source_path)
    name = (display_name or source.stem).strip() or source.stem
    destination_directory = _unique_destination(SCRIPTS_DIR, name)
    destination_directory.mkdir(parents=True, exist_ok=False)
    destination_file = destination_directory / source.name

    log("IMPORT", f"Copie du script vers : {destination_file}")
    try:
        shutil.copy2(source, destination_file)
    except Exception:
        shutil.rmtree(destination_directory, ignore_errors=True)
        raise

    item = LauncherItem.create_script(
        name=name,
        local_path=str(destination_file),
        source_path=str(source),
    )
    log("IMPORT", f"Script importé : {item.name} ({item.id})")
    return item


def import_project(
    source_directory: str | Path,
    entry_script: str,
    display_name: str | None = None,
) -> LauncherItem:
    """Copie un projet complet et valide son point d'entrée Python."""
    ensure_directories()
    source = Path(source_directory).expanduser().resolve()
    if not source.exists() or not source.is_dir():
        raise ImporterError(f"Dossier projet introuvable : {source}")

    python_files = discover_python_files(source)
    normalized_entry = Path(entry_script).as_posix().lstrip("/")
    if normalized_entry not in python_files:
        raise ImporterError(
            "Le point d'entrée choisi ne fait pas partie des fichiers Python détectés"
        )

    validate_python_file(source / normalized_entry)
    name = (display_name or source.name).strip() or source.name
    destination = _unique_destination(PROJECTS_DIR, name)

    log("IMPORT", f"Copie du projet {source} vers {destination}")
    try:
        shutil.copytree(
            source,
            destination,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".DS_Store"
            ),
        )
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise

    item = LauncherItem.create_project(
        name=name,
        local_path=str(destination),
        entry_script=normalized_entry,
        source_path=str(source),
    )
    log("IMPORT", f"Projet importé : {item.name} / entrée {normalized_entry}")
    return item


def rename_imported_folder(item: LauncherItem, new_name: str) -> LauncherItem:
    """Renomme le dossier physique associé à un élément sans toucher à son code."""
    clean_name = new_name.strip()
    if not clean_name:
        raise ImporterError("Le nouveau nom ne peut pas être vide")

    current = Path(item.local_path)
    current_root = current.parent if item.kind == "script" else current
    if not current_root.exists():
        raise ImporterError(f"Dossier local introuvable : {current_root}")

    target = _unique_destination(current_root.parent, clean_name)
    current_root.rename(target)
    new_local_path = str(target / current.name) if item.kind == "script" else str(target)

    updated = replace(item, name=clean_name, local_path=new_local_path)
    updated.validate()
    log("IMPORT", f"Élément renommé physiquement : {item.name} -> {clean_name}")
    return updated
