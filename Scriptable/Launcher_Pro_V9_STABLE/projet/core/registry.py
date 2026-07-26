"""Registre JSON robuste de la bibliothèque Launcher Pro."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from config import REGISTRY_FILENAME
from .logger import log
from .models import LauncherItem
from .paths import DATA_DIR, ensure_directories


@dataclass
class Registry:
    """Collection persistante d'éléments avec écriture atomique."""

    items: list[LauncherItem] = field(default_factory=list)
    path: Path = field(default_factory=lambda: DATA_DIR / REGISTRY_FILENAME)

    @classmethod
    def load(cls, path: Path | None = None) -> "Registry":
        ensure_directories()
        target = path or (DATA_DIR / REGISTRY_FILENAME)

        if not target.exists():
            log("REGISTRY", f"Aucun registre existant : création de {target}")
            registry = cls(path=target)
            registry.save()
            return registry

        log("REGISTRY", f"Lecture de {target}")
        try:
            raw = json.loads(target.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Registre JSON illisible : {exc}") from exc

        if not isinstance(raw, dict) or not isinstance(raw.get("items", []), list):
            raise ValueError("Format de registre invalide")

        items = [LauncherItem.from_dict(entry) for entry in raw.get("items", [])]
        registry = cls(items=items, path=target)
        registry._assert_unique_ids()
        log("REGISTRY", f"{len(items)} élément(s) chargé(s)")
        return registry

    def save(self) -> None:
        ensure_directories()
        self._assert_unique_ids()
        payload = {
            "schema_version": 1,
            "items": [item.to_dict() for item in self.items],
        }
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(text, encoding="utf-8")
        os.replace(temporary, self.path)
        log("REGISTRY", f"Registre enregistré : {len(self.items)} élément(s)")

    def _assert_unique_ids(self) -> None:
        ids = [item.id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("Le registre contient des identifiants en double")

    def all(self) -> list[LauncherItem]:
        return list(self.items)

    def require(self, item_id: str) -> LauncherItem:
        for item in self.items:
            if item.id == item_id:
                return item
        raise KeyError(f"Élément introuvable : {item_id}")

    def add(self, item: LauncherItem) -> LauncherItem:
        if any(existing.id == item.id for existing in self.items):
            raise ValueError(f"Identifiant déjà présent : {item.id}")
        item.validate()
        self.items.append(item)
        self.save()
        log("REGISTRY", f"Ajout : {item.kind} · {item.name}")
        return item

    def update(self, item: LauncherItem) -> LauncherItem:
        item.validate()
        for index, existing in enumerate(self.items):
            if existing.id == item.id:
                item.touch()
                self.items[index] = item
                self.save()
                log("REGISTRY", f"Mise à jour : {item.kind} · {item.name}")
                return item
        raise KeyError(f"Élément introuvable : {item.id}")

    def remove(self, item_id: str) -> LauncherItem:
        item = self.require(item_id)
        self.items = [candidate for candidate in self.items if candidate.id != item_id]
        self.save()
        log("REGISTRY", f"Suppression du registre : {item.kind} · {item.name}")
        return item

    def search(self, query: str = "", kind: str | None = None) -> list[LauncherItem]:
        normalized = query.strip().casefold()
        result: Iterable[LauncherItem] = self.items

        if kind is not None:
            if kind not in {"script", "project"}:
                raise ValueError(f"Filtre de type invalide : {kind}")
            result = (item for item in result if item.kind == kind)

        if normalized:
            result = (
                item
                for item in result
                if normalized in item.name.casefold()
                or normalized in item.category.casefold()
                or normalized in item.entry_script.casefold()
            )

        return sorted(
            result,
            key=lambda item: (not item.favorite, item.name.casefold(), item.created_at),
        )
