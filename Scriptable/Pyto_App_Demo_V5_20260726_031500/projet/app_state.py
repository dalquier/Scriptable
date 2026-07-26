from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List


class AppState:
    """Persistance légère et thread-safe pour la démonstration."""

    DEFAULT_STATE: Dict[str, Any] = {
        "launch_count": 0,
        "action_count": 0,
        "dark_mode": "auto",
        "notifications_enabled": True,
        "display_name": "Damien",
        "activities": [],
    }

    def __init__(self, root_dir: Path) -> None:
        self._lock = RLock()
        self.data_dir = root_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.data_dir / "app_state.json"
        self._state = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return dict(self.DEFAULT_STATE)
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            merged = dict(self.DEFAULT_STATE)
            if isinstance(raw, dict):
                merged.update(raw)
            if not isinstance(merged.get("activities"), list):
                merged["activities"] = []
            return merged
        except (OSError, ValueError, TypeError):
            return dict(self.DEFAULT_STATE)

    def save(self) -> None:
        with self._lock:
            temp_path = self.path.with_suffix(".tmp")
            payload = json.dumps(self._state, ensure_ascii=False, indent=2, sort_keys=True)
            temp_path.write_text(payload, encoding="utf-8")
            temp_path.replace(self.path)

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return json.loads(json.dumps(self._state, ensure_ascii=False))

    def register_launch(self) -> Dict[str, Any]:
        with self._lock:
            self._state["launch_count"] = int(self._state.get("launch_count", 0)) + 1
            self._append_activity_locked("Application ouverte", "system")
            self.save()
            return self.snapshot()

    def register_action(self, title: str = "Action principale exécutée") -> Dict[str, Any]:
        with self._lock:
            self._state["action_count"] = int(self._state.get("action_count", 0)) + 1
            self._append_activity_locked(title, "success")
            self.save()
            return self.snapshot()

    def set_preference(self, key: str, value: Any) -> Dict[str, Any]:
        allowed = {"dark_mode", "notifications_enabled", "display_name"}
        if key not in allowed:
            raise ValueError(f"Préférence non autorisée : {key}")
        with self._lock:
            self._state[key] = value
            self._append_activity_locked(f"Réglage modifié : {key}", "info")
            self.save()
            return self.snapshot()

    def add_activity(self, title: str, kind: str = "info") -> Dict[str, Any]:
        with self._lock:
            self._append_activity_locked(title, kind)
            self.save()
            return self.snapshot()

    def _append_activity_locked(self, title: str, kind: str) -> None:
        activities: List[Dict[str, str]] = self._state.setdefault("activities", [])
        activities.insert(0, {"title": str(title), "kind": str(kind), "timestamp": datetime.now().isoformat(timespec="seconds")})
        del activities[30:]

    def reset(self) -> Dict[str, Any]:
        with self._lock:
            self._state = dict(self.DEFAULT_STATE)
            self._append_activity_locked("Données réinitialisées", "warning")
            self.save()
            return self.snapshot()
