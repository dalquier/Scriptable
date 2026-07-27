# -*- coding: utf-8 -*-
"""Réglages locaux de Codex Reader v8."""

import json
from pathlib import Path

APP_DIR = Path.home() / "Documents" / "CodexReaderV8"
SETTINGS_FILE = APP_DIR / "settings.json"


def load_settings():
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"last_url": ""}


def save_settings(data):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
