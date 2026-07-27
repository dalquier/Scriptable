# -*- coding: utf-8 -*-
"""Persistance locale de Codex Reader v9."""

import json
from pathlib import Path


APP_DIR = Path.home() / "Documents" / "CodexReaderV9"
SETTINGS_FILE = APP_DIR / "settings.json"
DIAGNOSTICS_DIR = APP_DIR / "Diagnostics"


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


def save_diagnostic(name, content):
    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    path = DIAGNOSTICS_DIR / name
    path.write_text(content, encoding="utf-8")
    return path
