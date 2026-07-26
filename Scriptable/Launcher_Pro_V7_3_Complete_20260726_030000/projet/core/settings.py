from __future__ import annotations

import json
from typing import Any

from .paths import SETTINGS_FILE, ensure_directories

DEFAULT_SETTINGS = {
    "schema_version": 1,
    "default_category": "Général",
    "keep_source_path": True,
    "auto_backup_registry": True,
    "presentation": "sheet",
}


def load_settings() -> dict[str, Any]:
    ensure_directories()
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return dict(DEFAULT_SETTINGS)
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        result = dict(DEFAULT_SETTINGS)
        if isinstance(data, dict):
            result.update(data)
        return result
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict[str, Any]) -> None:
    ensure_directories()
    SETTINGS_FILE.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
