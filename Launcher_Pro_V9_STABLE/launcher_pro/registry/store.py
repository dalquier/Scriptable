"""Atomic JSON persistence for the launcher library."""

import json
import os
import tempfile
from dataclasses import replace
from pathlib import Path
from typing import Iterable, List, Optional

from .models import LibraryItem


class RegistryError(RuntimeError):
    """Raised when the registry cannot be read or updated."""


class LibraryRegistry:
    def __init__(self, path: Path):
        self.path = Path(path)

    def all(self) -> List[LibraryItem]:
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                raise ValueError("the root must be a list")
            return [LibraryItem.from_dict(item) for item in raw]
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise RegistryError("La bibliothèque est illisible : {}".format(exc)) from exc

    def find(self, item_id: str) -> Optional[LibraryItem]:
        return next((item for item in self.all() if item.id == item_id), None)

    def add(self, item: LibraryItem) -> LibraryItem:
        items = self.all()
        if any(existing.entrypoint == item.entrypoint for existing in items):
            raise RegistryError("Ce point d'entrée est déjà dans la bibliothèque.")
        items.append(item)
        self._save(items)
        return item

    def rename(self, item_id: str, name: str) -> LibraryItem:
        clean_name = name.strip()
        if not clean_name:
            raise RegistryError("Le nom ne peut pas être vide.")
        return self._replace(item_id, name=clean_name)

    def toggle_favorite(self, item_id: str) -> LibraryItem:
        item = self._required(item_id)
        return self._replace(item_id, favorite=not item.favorite)

    def remove(self, item_id: str) -> None:
        items = self.all()
        remaining = [item for item in items if item.id != item_id]
        if len(remaining) == len(items):
            raise RegistryError("Élément introuvable.")
        self._save(remaining)

    def _required(self, item_id: str) -> LibraryItem:
        item = self.find(item_id)
        if item is None:
            raise RegistryError("Élément introuvable.")
        return item

    def _replace(self, item_id: str, **changes: object) -> LibraryItem:
        items = self.all()
        updated = replace(self._required(item_id), **changes)
        self._save(updated if item.id == item_id else item for item in items)
        return updated

    def _save(self, items: Iterable[LibraryItem]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2)
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(self.path.parent), delete=False) as temp:
                temp.write(payload)
                temp.flush()
                os.fsync(temp.fileno())
                temp_name = temp.name
            os.replace(temp_name, self.path)
        except OSError as exc:
            if temp_name:
                Path(temp_name).unlink(missing_ok=True)
            raise RegistryError("Impossible d'enregistrer la bibliothèque : {}".format(exc)) from exc
