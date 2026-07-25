from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SCRIPTS_DIR = DATA_DIR / "scripts"
LOGS_DIR = DATA_DIR / "logs"
BACKUPS_DIR = DATA_DIR / "backups"
REGISTRY_FILE = DATA_DIR / "registry.json"
HISTORY_FILE = DATA_DIR / "history.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
LOG_FILE = LOGS_DIR / "launcher.log"


def ensure_directories() -> None:
    for path in (DATA_DIR, SCRIPTS_DIR, LOGS_DIR, BACKUPS_DIR):
        path.mkdir(parents=True, exist_ok=True)
