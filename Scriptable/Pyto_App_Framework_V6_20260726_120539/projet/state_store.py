from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_STATE = {
    "display_name": "Damien",
    "theme": "system",
    "launch_count": 0,
    "action_count": 0,
    "last_action": "Aucune",
    "activity": [],
}


class StateStore:
    def __init__(self, root_dir: Path) -> None:
        self.path = root_dir / "app_state.json"
        self.state = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return deepcopy(DEFAULT_STATE)
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            state = deepcopy(DEFAULT_STATE)
            if isinstance(loaded, dict):
                state.update(loaded)
            return state
        except Exception:
            return deepcopy(DEFAULT_STATE)

    def save(self) -> None:
        self.path.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def register_launch(self) -> None:
        self.state["launch_count"] = int(self.state.get("launch_count", 0)) + 1
        self.add_activity("Application ouverte", count_action=False)

    def add_activity(self, label: str, count_action: bool = True) -> None:
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.state["last_action"] = label
        if count_action:
            self.state["action_count"] = int(self.state.get("action_count", 0)) + 1
        activity = list(self.state.get("activity", []))
        activity.insert(0, {"label": label, "date": now})
        self.state["activity"] = activity[:20]
        self.save()

    def update_preference(self, key: str, value: Any) -> None:
        if key not in {"display_name", "theme"}:
            raise ValueError(f"Préférence non autorisée : {key}")
        self.state[key] = value
        self.add_activity(f"Préférence modifiée : {key}")

    def reset(self) -> None:
        self.state = deepcopy(DEFAULT_STATE)
        self.add_activity("Données réinitialisées", count_action=False)

    def snapshot(self) -> dict[str, Any]:
        return deepcopy(self.state)
