from __future__ import annotations

from datetime import datetime

from .paths import LOG_FILE, ensure_directories


def log(message: str, level: str = "INFO") -> None:
    ensure_directories()
    line = f"[{datetime.now().isoformat(timespec='seconds')}] [{level}] {message}\n"
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line)


def read_log() -> str:
    ensure_directories()
    return LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else ""
