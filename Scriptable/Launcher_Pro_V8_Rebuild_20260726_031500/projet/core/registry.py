from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional

from .models import LauncherItem, utc_now
from .paths import REGISTRY_FILE, ensure_directories


class Registry:
    def __init__(self, items: Optional[Iterable[LauncherItem]] = None, path: Path = REGISTRY_FILE) -> None:
        self.items = list(items or [])
        self.path = path

    @classmethod
    def load(cls, path: Path = REGISTRY_FILE) -> "Registry":
        ensure_directories()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            payload = {"version": 1, "items": []}
        return cls([LauncherItem.from_dict(x) for x in payload.get("items", [])], path)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(self.path.suffix + ".tmp")
        temp.write_text(json.dumps({"version": 1, "items": [x.to_dict() for x in self.items]}, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(self.path)

    def add(self, item: LauncherItem) -> None:
        if self.get(item.id):
            raise ValueError("Identifiant déjà présent")
        self.items.append(item)
        self.save()

    def update(self, item: LauncherItem) -> None:
        item.updated_at = utc_now()
        for index, current in enumerate(self.items):
            if current.id == item.id:
                self.items[index] = item
                self.save()
                return
        raise KeyError(item.id)

    def remove(self, item_id: str) -> None:
        self.items = [x for x in self.items if x.id != item_id]
        self.save()

    def get(self, item_id: str) -> Optional[LauncherItem]:
        return next((x for x in self.items if x.id == item_id), None)

    def require(self, item_id: str) -> LauncherItem:
        item = self.get(item_id)
        if item is None:
            raise KeyError(item_id)
        return item

    def search(self, query: str = "", kind: Optional[str] = None) -> list[LauncherItem]:
        q = query.strip().lower()
        result = [x for x in self.items if (not kind or x.kind == kind) and (not q or q in x.name.lower() or q in x.category.lower())]
        return sorted(result, key=lambda x: (not x.favorite, x.name.lower()))
