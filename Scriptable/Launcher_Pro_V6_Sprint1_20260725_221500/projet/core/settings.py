from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Dict

from .paths import SETTINGS_FILE, ensure_directories

DEFAULT_SETTINGS: Dict[str, Any] = {
    "schema_version": 1,
    "default_category": "Général",
    "sort_mode": "favorite_name",
    "keep_source_path": True,
    "capture_output": True,
    "max_history_entries": 500,
    "auto_backup_registry": True
}


def load_settings() -> Dict[str, Any]:
    ensure_directories()
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return deepcopy(DEFAULT_SETTINGS)
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    merged = deepcopy(DEFAULT_SETTINGS)
    if isinstance(data, dict):
        merged.update(data)
    return merged


def save_settings(settings: Dict[str, Any]) -> None:
    ensure_directories()
    temp = SETTINGS_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(SETTINGS_FILE)
