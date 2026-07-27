# -*- coding: utf-8 -*-
"""Réglages, historique et exports."""

import json
from datetime import datetime
from pathlib import Path

APP_DIR = Path.home() / "Documents" / "CodexReaderV6"
SETTINGS_FILE = APP_DIR / "settings.json"
HISTORY_FILE = APP_DIR / "history.json"
EXPORT_DIR = APP_DIR / "Exports"


def ensure_dirs():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path, value):
    ensure_dirs()
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def load_settings():
    return load_json(SETTINGS_FILE, {"last_url": "", "auto_open_last": True})


def save_settings(value):
    save_json(SETTINGS_FILE, value)


def add_history(url, title):
    history = load_json(HISTORY_FILE, [])
    history = [item for item in history if item.get("url") != url]
    history.insert(0, {"url": url, "title": title, "date": datetime.now().astimezone().isoformat(timespec="seconds")})
    save_json(HISTORY_FILE, history[:30])


def export_pair(question, answer, source_url):
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md = EXPORT_DIR / f"codex_{stamp}.md"
    txt = EXPORT_DIR / f"codex_{stamp}.txt"
    md.write_text(f"# Export Codex\n\nSource : {source_url}\n\n## Question\n\n{question}\n\n## Réponse\n\n{answer}\n", encoding="utf-8")
    txt.write_text(f"SOURCE\n{source_url}\n\nQUESTION\n{'='*40}\n{question}\n\nRÉPONSE\n{'='*40}\n{answer}\n", encoding="utf-8")
    return md, txt
