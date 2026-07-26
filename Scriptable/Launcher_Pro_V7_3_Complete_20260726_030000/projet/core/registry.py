from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import LauncherItem, utc_now
from .paths import BACKUPS_DIR, REGISTRY_FILE, ensure_directories


class Registry:
    def __init__(self, items: Iterable[LauncherItem] = ()) -> None:
        self.items = list(items)

    @classmethod
    def load(cls) -> "Registry":
        ensure_directories()
        if not REGISTRY_FILE.exists():
            REGISTRY_FILE.write_text('{"version": 1, "items": []}', encoding="utf-8")
            return cls()
        try:
            data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
            raw_items = data.get("items", []) if isinstance(data, dict) else []
            return cls(LauncherItem.from_dict(item) for item in raw_items if isinstance(item, dict))
        except Exception:
            return cls()

    def save(self) -> None:
        ensure_directories()
        if REGISTRY_FILE.exists():
            stamp = datetime.now().isoformat(timespec="seconds").replace(":", "-")
            shutil.copy2(REGISTRY_FILE, BACKUPS_DIR / f"registry_{stamp}.json")
        payload = {"version": 1, "items": [item.to_dict() for item in self.items]}
        temp = REGISTRY_FILE.with_suffix(".json.tmp")
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(REGISTRY_FILE)

    def add(self, item: LauncherItem) -> LauncherItem:
        if any(existing.id == item.id for existing in self.items):
            raise ValueError(f"Identifiant déjà présent : {item.id}")
        item.updated_at = utc_now()
        self.items.append(item)
        self.save()
        return item

    def update(self, item: LauncherItem) -> LauncherItem:
        for index, existing in enumerate(self.items):
            if existing.id == item.id:
                item.updated_at = utc_now()
                self.items[index] = item
                self.save()
                return item
        raise KeyError(item.id)

    def remove(self, item_id: str) -> LauncherItem:
        for index, item in enumerate(self.items):
            if item.id == item_id:
                removed = self.items.pop(index)
                self.save()
                return removed
        raise KeyError(item_id)

    def require(self, item_id: str) -> LauncherItem:
        for item in self.items:
            if item.id == item_id:
                return item
        raise KeyError(f"Élément introuvable : {item_id}")

    def search(self, query: str = "", kind: str | None = None) -> list[LauncherItem]:
        needle = query.strip().lower()
        result = []
        for item in self.items:
            if kind and item.kind != kind:
                continue
            haystack = f"{item.name} {item.category} {item.entry_script}".lower()
            if needle and needle not in haystack:
                continue
            result.append(item)
        return sorted(result, key=lambda item: (not item.favorite, item.name.lower()))
