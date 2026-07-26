"""Registre JSON robuste et atomique de la bibliothèque Launcher Pro."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, TypeVar

from config import REGISTRY_FILENAME
from .logger import log
from .models import LauncherItem
from .paths import DATA_DIR, ensure_directories

_SCHEMA_VERSION = 1
_T = TypeVar("_T")


class RegistryError(RuntimeError):
    """Erreur de lecture ou d'écriture du registre persistant."""


@dataclass
class Registry:
    """Collection d'éléments dont chaque mutation est persistée atomiquement."""

    items: list[LauncherItem] = field(default_factory=list)
    path: Path = field(default_factory=lambda: DATA_DIR / REGISTRY_FILENAME)

    @classmethod
    def load(cls, path: Path | None = None) -> "Registry":
        ensure_directories()
        target = Path(path) if path is not None else DATA_DIR / REGISTRY_FILENAME
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            registry = cls(path=target)
            registry.save()
            return registry
        try:
            raw = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise RegistryError(f"Registre JSON illisible : {exc}") from exc
        if not isinstance(raw, dict) or not isinstance(raw.get("items"), list):
            raise RegistryError("Format de registre invalide")
        if raw.get("schema_version") != _SCHEMA_VERSION:
            raise RegistryError("Version de registre non prise en charge")
        try:
            registry = cls(
                items=[LauncherItem.from_dict(entry) for entry in raw["items"]],
                path=target,
            )
            registry._assert_unique_ids()
        except (TypeError, ValueError, KeyError) as exc:
            raise RegistryError(f"Contenu de registre invalide : {exc}") from exc
        log("REGISTRY", f"{len(registry.items)} élément(s) chargé(s)")
        return registry

    def save(self) -> None:
        """Écrit un JSON complet via un fichier temporaire synchronisé."""
        self._assert_unique_ids()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"schema_version": _SCHEMA_VERSION, "items": [item.to_dict() for item in self.items]}
        temporary: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.path.parent, delete=False
            ) as stream:
                json.dump(payload, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
                temporary = stream.name
            os.replace(temporary, self.path)
        except OSError as exc:
            if temporary is not None:
                Path(temporary).unlink(missing_ok=True)
            raise RegistryError(f"Écriture du registre impossible : {exc}") from exc

    def _assert_unique_ids(self) -> None:
        ids = [item.id for item in self.items]
        if len(ids) != len(set(ids)):
            raise RegistryError("Le registre contient des identifiants en double")

    def all(self) -> list[LauncherItem]:
        return list(self.items)

    def require(self, item_id: str) -> LauncherItem:
        for item in self.items:
            if item.id == item_id:
                return item
        raise KeyError(f"Élément introuvable : {item_id}")

    def add(self, item: LauncherItem) -> LauncherItem:
        if any(existing.id == item.id for existing in self.items):
            raise RegistryError(f"Identifiant déjà présent : {item.id}")
        item.validate()
        return self._mutate(lambda: (self.items.append(item), item)[1])

    def update(self, item: LauncherItem) -> LauncherItem:
        item.validate()
        for index, existing in enumerate(self.items):
            if existing.id == item.id:
                item.touch()
                return self._mutate(lambda: self._replace(index, item))
        raise KeyError(f"Élément introuvable : {item.id}")

    def _replace(self, index: int, item: LauncherItem) -> LauncherItem:
        self.items[index] = item
        return item

    def remove(self, item_id: str) -> LauncherItem:
        item = self.require(item_id)
        return self._mutate(lambda: self._remove(item))

    def _remove(self, item: LauncherItem) -> LauncherItem:
        self.items = [candidate for candidate in self.items if candidate.id != item.id]
        return item

    def _mutate(self, operation: Callable[[], _T]) -> _T:
        snapshot = list(self.items)
        try:
            result = operation()
            self.save()
            return result
        except BaseException:
            self.items = snapshot
            raise

    def search(self, query: str = "", kind: str | None = None) -> list[LauncherItem]:
        normalized = query.strip().casefold()
        result: Iterable[LauncherItem] = self.items
        if kind is not None:
            if kind not in {"script", "project"}:
                raise ValueError(f"Filtre de type invalide : {kind}")
            result = (item for item in result if item.kind == kind)
        if normalized:
            result = (
                item for item in result
                if normalized in item.name.casefold()
                or normalized in item.category.casefold()
                or normalized in item.entry_script.casefold()
            )
        return sorted(result, key=lambda item: (not item.favorite, item.name.casefold(), item.created_at))
