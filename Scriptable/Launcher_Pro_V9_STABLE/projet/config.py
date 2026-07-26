"""Configuration centrale de Launcher Pro V9.

Les options de diagnostic sont regroupées ici pour éviter les valeurs cachées
dans les modules de l'application.
"""

from __future__ import annotations

APP_NAME = "Launcher Pro"
APP_VERSION = "9.0.0-alpha.1"

# Affiche les traces dans le terminal Pyto et les écrit dans logs/launcher.log.
DEBUG = True

# Taille maximale du journal. Au-delà, le fichier est archivé automatiquement.
MAX_LOG_BYTES = 1_000_000

# Nombre maximal d'archives de journal conservées.
LOG_BACKUP_COUNT = 3

# Noms des fichiers de données persistantes.
REGISTRY_FILENAME = "registry.json"
HISTORY_FILENAME = "history.jsonl"

# Dossiers ignorés lors de la copie d'un projet Python.
IGNORED_PROJECT_NAMES = {
    ".git",
    ".github",
    ".DS_Store",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}

# Extensions ignorées pendant la copie d'un projet.
IGNORED_PROJECT_SUFFIXES = {".pyc", ".pyo"}
