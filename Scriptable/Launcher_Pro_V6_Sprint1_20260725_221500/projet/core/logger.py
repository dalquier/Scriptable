from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .paths import LOG_FILE, ensure_directories


def log(message: str, level: str = "INFO") -> None:
    ensure_directories()
    stamp = datetime.now().isoformat(timespec="seconds")
    line = f"[{stamp}] [{level.upper()}] {message}\n"
    Path(LOG_FILE).open("a", encoding="utf-8").write(line)


def read_log(max_chars: int = 12000) -> str:
    if not LOG_FILE.exists():
        return ""
    text = LOG_FILE.read_text(encoding="utf-8", errors="replace")
    return text[-max_chars:]
