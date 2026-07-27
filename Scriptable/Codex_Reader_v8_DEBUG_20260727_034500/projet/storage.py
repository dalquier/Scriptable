# -*- coding: utf-8 -*-
"""Stockage local des réglages et diagnostics."""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path.home() / "Documents" / "CodexReaderDebug"
DIAG_DIR = ROOT / "Diagnostics"
SETTINGS = ROOT / "settings.json"


def ensure_dirs():
    ROOT.mkdir(parents=True, exist_ok=True)
    DIAG_DIR.mkdir(parents=True, exist_ok=True)


def load_settings():
    ensure_dirs()
    try:
        return json.loads(SETTINGS.read_text(encoding="utf-8"))
    except Exception:
        return {"last_url": ""}


def save_settings(data):
    ensure_dirs()
    SETTINGS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def save_diagnostic(payload, html_text):
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = DIAG_DIR / f"diagnostic_{stamp}.json"
    html_path = DIAG_DIR / f"page_{stamp}.html"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    html_path.write_text(html_text or "", encoding="utf-8")
    return json_path, html_path
