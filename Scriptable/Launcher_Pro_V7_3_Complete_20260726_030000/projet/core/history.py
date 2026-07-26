from __future__ import annotations

import json

from .models import LauncherItem, RunnerResult
from .paths import HISTORY_FILE, ensure_directories


def load_history() -> list[dict]:
    ensure_directories()
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")
        return []
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def append_history(item: LauncherItem, result: RunnerResult) -> None:
    history = load_history()
    history.insert(0, {
        "date": item.last_run_at,
        "item_id": item.id,
        "item_name": item.name,
        "kind": item.kind,
        "duration": item.last_duration,
        "status": item.last_status,
        "error": result.error,
        "output": result.output[-4000:],
    })
    HISTORY_FILE.write_text(json.dumps(history[:200], ensure_ascii=False, indent=2), encoding="utf-8")
