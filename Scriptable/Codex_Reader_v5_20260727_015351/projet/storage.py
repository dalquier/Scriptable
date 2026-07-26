# -*- coding: utf-8 -*-
"""Persistance légère et exports de Codex Reader."""

import json
from datetime import datetime
from pathlib import Path


APP_DIR = Path.home() / "Documents" / "CodexReader"
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


def save_json(path, data):
    ensure_dirs()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_settings():
    return load_json(SETTINGS_FILE, {"last_url": "", "max_history": 20})


def save_settings(settings):
    save_json(SETTINGS_FILE, settings)


def add_history(url, title=""):
    if not url:
        return
    settings = load_settings()
    limit = int(settings.get("max_history", 20))
    history = load_json(HISTORY_FILE, [])
    history = [item for item in history if item.get("url") != url]
    history.insert(0, {
        "url": url,
        "title": title,
        "opened_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    })
    save_json(HISTORY_FILE, history[:limit])


def export_markdown(question, answer, source_url=""):
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = EXPORT_DIR / f"codex_{stamp}.md"
    content = (
        "# Export Codex\n\n"
        f"Source : {source_url}\n\n"
        "## Question\n\n"
        f"{question}\n\n"
        "## Réponse\n\n"
        f"{answer}\n"
    )
    path.write_text(content, encoding="utf-8")
    return path


def export_text(question, answer, source_url=""):
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = EXPORT_DIR / f"codex_{stamp}.txt"
    content = (
        f"SOURCE\n{source_url}\n\n"
        f"QUESTION\n{'=' * 40}\n{question}\n\n"
        f"RÉPONSE\n{'=' * 40}\n{answer}\n"
    )
    path.write_text(content, encoding="utf-8")
    return path
