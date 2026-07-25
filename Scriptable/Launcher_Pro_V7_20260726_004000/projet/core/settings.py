from __future__ import annotations

import json
from typing import Any, Dict

from .paths import SETTINGS_FILE, ensure_directories

DEFAULTS: Dict[str, Any] = {
    "schema_version": 1,
    "default_category": "Général",
    "keep_source_path": True,
    "auto_backup_registry": True,
    "presentation": "sheet",
}


def load_settings() -> Dict[str, Any]:
    ensure_directories()
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULTS.copy())
        return DEFAULTS.copy()
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULTS.copy()
    merged = DEFAULTS.copy()
    if isinstance(data, dict):
        merged.update(data)
    return merged


def save_settings(settings: Dict[str, Any]) -> None:
    ensure_directories()
    SETTINGS_FILE.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
