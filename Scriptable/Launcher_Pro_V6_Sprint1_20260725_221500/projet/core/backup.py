from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from .logger import log
from .paths import BACKUPS_DIR, REGISTRY_FILE, ensure_directories


def create_registry_backup() -> Optional[Path]:
    ensure_directories()
    if not REGISTRY_FILE.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    target = BACKUPS_DIR / f"registry_{stamp}.json"
    shutil.copy2(REGISTRY_FILE, target)
    log(f"Sauvegarde du registre créée : {target.name}")
    return target


def list_backups() -> list[Path]:
    ensure_directories()
    return sorted(BACKUPS_DIR.glob("registry_*.json"), reverse=True)


def restore_latest_backup() -> Optional[Path]:
    backups = list_backups()
    if not backups:
        return None
    shutil.copy2(backups[0], REGISTRY_FILE)
    log(f"Registre restauré depuis {backups[0].name}", "WARNING")
    return backups[0]
