"""Journalisation vers le terminal Pyto et un fichier persistant."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from threading import RLock

from config import DEBUG, LOG_BACKUP_COUNT, MAX_LOG_BYTES
from .paths import LOGS_DIR, ensure_directories

_LOCK = RLock()
_LOG_FILE = LOGS_DIR / "launcher.log"


def _rotate_if_needed() -> None:
    """Archive le journal lorsqu'il dépasse la taille configurée."""

    if not _LOG_FILE.exists() or _LOG_FILE.stat().st_size < MAX_LOG_BYTES:
        return

    oldest = LOGS_DIR / f"launcher.log.{LOG_BACKUP_COUNT}"
    if oldest.exists():
        oldest.unlink()

    for index in range(LOG_BACKUP_COUNT - 1, 0, -1):
        source = LOGS_DIR / f"launcher.log.{index}"
        target = LOGS_DIR / f"launcher.log.{index + 1}"
        if source.exists():
            source.replace(target)

    _LOG_FILE.replace(LOGS_DIR / "launcher.log.1")


def log(section: str, message: str, *, force: bool = False) -> None:
    """Écrit une trace horodatée.

    `force=True` permet d'afficher les erreurs même lorsque DEBUG est désactivé.
    """

    if not DEBUG and not force:
        return

    ensure_directories()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    line = f"[{timestamp}] [{section.upper()}] {message}"

    with _LOCK:
        _rotate_if_needed()
        print(line, file=sys.stdout, flush=True)
        with _LOG_FILE.open("a", encoding="utf-8") as stream:
            stream.write(line + "\n")


def log_exception(section: str, exc: BaseException) -> None:
    """Journalise une exception sous une forme lisible dans le terminal."""

    log(section, f"{type(exc).__name__}: {exc}", force=True)


def log_path() -> Path:
    """Renvoie le chemin du fichier de journal courant."""

    ensure_directories()
    return _LOG_FILE
