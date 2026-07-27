# -*- coding: utf-8 -*-
"""Persistance minimale de Codex Reader v10."""

import json
from pathlib import Path

SETTINGS_PATH = Path.home() / "Documents" / "CodexReaderV10" / "settings.json"


def load_settings():
    try:
        if SETTINGS_PATH.exists():
            return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def save_settings(data):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(
        json.dumps(data or {}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
