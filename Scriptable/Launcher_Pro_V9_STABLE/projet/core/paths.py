"""Chemins de stockage de Launcher Pro V9.

Tous les chemins sont calculés à partir du dossier du projet. Le module ne dépend
pas de l'emplacement iCloud ou local choisi par l'utilisateur dans Pyto.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
LIBRARY_DIR = PROJECT_ROOT / "library"
SCRIPTS_DIR = LIBRARY_DIR / "scripts"
PROJECTS_DIR = LIBRARY_DIR / "projects"


def ensure_directories() -> None:
    """Crée tous les dossiers techniques nécessaires s'ils sont absents."""

    for directory in (
        DATA_DIR,
        LOGS_DIR,
        LIBRARY_DIR,
        SCRIPTS_DIR,
        PROJECTS_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)
