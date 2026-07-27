# -*- coding: utf-8 -*-
"""Réglages locaux de Codex Reader v7."""

import json
from pathlib import Path

APP_DIR = Path.home() / "Documents" / "CodexReaderV7"
SETTINGS_FILE = APP_DIR / "settings.json"


def load_settings():
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"last_url": "", "auto_open_last": False}


def save_settings(settings):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
