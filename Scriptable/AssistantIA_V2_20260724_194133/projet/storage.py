import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from config import CONVERSATIONS_PATH, INDEX_DB_PATH, SETTINGS_PATH


def load_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
    except Exception:
        return default
    return default


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
    temp_path.replace(path)


def load_settings(defaults: Dict[str, Any]) -> Dict[str, Any]:
    stored = load_json(SETTINGS_PATH, {})
    merged = dict(defaults)
    if isinstance(stored, dict):
        merged.update(stored)
    return merged


def save_settings(settings: Dict[str, Any]) -> None:
    save_json(SETTINGS_PATH, settings)


def load_conversations() -> List[Dict[str, Any]]:
    data = load_json(CONVERSATIONS_PATH, [])
    return data if isinstance(data, list) else []


def save_conversations(conversations: List[Dict[str, Any]]) -> None:
    save_json(CONVERSATIONS_PATH, conversations)


def open_index_db() -> sqlite3.Connection:
    INDEX_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(INDEX_DB_PATH))
    connection.row_factory = sqlite3.Row
    return connection
