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

from config import IGNORED_PROJECT_NAMES, IGNORED_PROJECT_SUFFIXES
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
        "__main__.py": 0,
        "main.py": 1,
        "app.py": 2,
        "run.py": 3,
        "launcher.py": 4,
        "start.py": 5,
    }
    return sorted(
        candidates,
        key=lambda value: (
            priorities.get(Path(value).name.casefold(), 100),
            value.count("/"),
            value.casefold(),
        ),
    )



def detect_entry_point(project_directory: str | Path) -> str:
    """Détecte sans ambiguïté le meilleur point d'entrée d'un projet."""
    root = Path(project_directory).expanduser().resolve()
    files = discover_python_files(root)
    if not files:
        raise ImporterError("Aucun fichier Python détecté dans le projet")
    ranked = suggest_entry_points(files)
    conventional = {"__main__.py", "main.py", "app.py", "run.py", "launcher.py", "start.py"}
    named = [value for value in ranked if Path(value).name.casefold() in conventional]
    if named:
        return named[0]
    guarded: list[str] = []
    for relative in files:
        source = (root / relative).read_text(encoding="utf-8-sig")
        try:
            tree = ast.parse(source, filename=relative)
        except SyntaxError:
            continue
        if any(
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == "__name__"
            and len(node.test.comparators) == 1
            and isinstance(node.test.comparators[0], ast.Constant)
            and node.test.comparators[0].value == "__main__"
            for node in ast.walk(tree)
        ):
            guarded.append(relative)
    if guarded:
        return guarded[0]
    if len(files) == 1:
        return files[0]
    raise ImporterError("Point d'entrée ambigu : une sélection explicite est nécessaire")

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
            ignore=lambda _directory, names: {
                name for name in names
                if name in IGNORED_PROJECT_NAMES
                or Path(name).suffix.casefold() in IGNORED_PROJECT_SUFFIXES
            },
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
