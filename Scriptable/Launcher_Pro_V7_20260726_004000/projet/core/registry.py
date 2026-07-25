from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional

from .logger import log
from .models import LauncherItem, utc_now
from .paths import BACKUPS_DIR, REGISTRY_FILE, ensure_directories


class Registry:
    def __init__(self, items: Optional[List[LauncherItem]] = None, schema_version: int = 2):
        self.items = items or []
        self.schema_version = schema_version

    @classmethod
    def load(cls) -> "Registry":
        ensure_directories()
        if not REGISTRY_FILE.exists():
            registry = cls()
            registry.save(create_backup=False)
            return registry
        try:
            data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        except Exception as exc:
            log(f"Registre illisible : {exc}", "ERROR")
            return cls()
        raw_items = data.get("items")
        if raw_items is None:
            raw_items = data.get("scripts", [])
        items = [LauncherItem.from_dict(item) for item in raw_items if isinstance(item, dict)]
        return cls(items=items, schema_version=int(data.get("schema_version", 2)))

    def save(self, create_backup: bool = True) -> None:
        ensure_directories()
        if create_backup and REGISTRY_FILE.exists():
            stamp = utc_now().replace(":", "-")
            backup = BACKUPS_DIR / f"registry_{stamp}.json"
            try:
                backup.write_text(REGISTRY_FILE.read_text(encoding="utf-8"), encoding="utf-8")
            except Exception:
                pass
        payload = {
            "schema_version": self.schema_version,
            "updated_at": utc_now(),
            "items": [item.to_dict() for item in self.items],
        }
        temp = REGISTRY_FILE.with_suffix(".tmp")
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(REGISTRY_FILE)
        log(f"Registre enregistré : {len(self.items)} élément(s)")

    def add(self, item: LauncherItem) -> LauncherItem:
        if self.get(item.id):
            raise ValueError(f"Identifiant déjà présent : {item.id}")
        self.items.append(item)
        self.save()
        return item

    def get(self, item_id: str) -> Optional[LauncherItem]:
        return next((item for item in self.items if item.id == item_id), None)

    def require(self, item_id: str) -> LauncherItem:
        item = self.get(item_id)
        if item is None:
            raise KeyError(f"Élément inconnu : {item_id}")
        return item

    def update(self, item: LauncherItem) -> None:
        item.updated_at = utc_now()
        self.save()

    def remove(self, item_id: str, delete_local_file: bool = True) -> LauncherItem:
        item = self.require(item_id)
        self.items = [entry for entry in self.items if entry.id != item_id]
        self.save()
        if delete_local_file and item.kind == "script" and item.local_path:
            try:
                Path(item.local_path).unlink(missing_ok=True)
            except OSError:
                pass
        return item

    def search(self, query: str = "", kind: Optional[str] = None) -> List[LauncherItem]:
        needle = query.strip().lower()
        items: Iterable[LauncherItem] = self.items
        if kind:
            items = [item for item in items if item.kind == kind]
        if needle:
            items = [item for item in items if needle in item.name.lower() or needle in item.category.lower()]
        return sorted(items, key=lambda item: (not item.favorite, item.name.lower()))
