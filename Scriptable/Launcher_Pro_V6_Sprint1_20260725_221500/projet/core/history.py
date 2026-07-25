from __future__ import annotations

import json
from typing import Any, Dict, List

from .paths import HISTORY_FILE, ensure_directories
from .settings import load_settings


def load_history() -> List[Dict[str, Any]]:
    ensure_directories()
    if not HISTORY_FILE.exists():
        save_history([])
        return []
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_history(entries: List[Dict[str, Any]]) -> None:
    ensure_directories()
    limit = int(load_settings().get("max_history_entries", 500))
    payload = entries[-limit:]
    temp = HISTORY_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(HISTORY_FILE)


def append_history(entry: Dict[str, Any]) -> None:
    entries = load_history()
    entries.append(entry)
    save_history(entries)
