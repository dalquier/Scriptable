from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SCRIPTS_DIR = DATA_DIR / "scripts"
PROJECTS_DIR = DATA_DIR / "projects"
LOGS_DIR = DATA_DIR / "logs"
REGISTRY_FILE = DATA_DIR / "registry.json"
HISTORY_FILE = DATA_DIR / "history.json"


def ensure_directories() -> None:
    for path in (DATA_DIR, SCRIPTS_DIR, PROJECTS_DIR, LOGS_DIR):
        path.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_FILE.exists():
        REGISTRY_FILE.write_text('{"version": 1, "items": []}\n', encoding="utf-8")
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text('{"version": 1, "runs": []}\n', encoding="utf-8")
