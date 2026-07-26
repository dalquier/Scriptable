from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STATE: dict[str, Any] = {
    "version": 1,
    "status": "ready",
    "iteration": 0,
    "active_branch": None,
    "active_goal": None,
    "last_commit": None,
    "last_pr": None,
    "blocked_reason": None,
    "history": [],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        state = dict(DEFAULT_STATE)
        save_state(path, state)
        return state
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Le fichier d'état doit contenir un objet JSON")
    merged = dict(DEFAULT_STATE)
    merged.update(data)
    return merged


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(state)
    payload["updated_at"] = utc_now()
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def record_event(state: dict[str, Any], kind: str, **details: Any) -> None:
    state.setdefault("history", []).append({"time": utc_now(), "kind": kind, **details})
    state["history"] = state["history"][-500:]
