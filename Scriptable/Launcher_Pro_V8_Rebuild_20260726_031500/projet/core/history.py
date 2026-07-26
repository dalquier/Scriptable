from __future__ import annotations

import json

from .models import LauncherItem, RunnerResult, utc_now
from .paths import HISTORY_FILE, ensure_directories


def append_history(item: LauncherItem, result: RunnerResult) -> None:
    ensure_directories()
    try:
        payload = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        payload = {"version": 1, "runs": []}
    payload.setdefault("runs", []).append({
        "time": utc_now(),
        "item_id": item.id,
        "name": item.name,
        "kind": item.kind,
        "success": result.success,
        "duration": result.duration,
        "error": result.error,
    })
    payload["runs"] = payload["runs"][-500:]
    HISTORY_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
