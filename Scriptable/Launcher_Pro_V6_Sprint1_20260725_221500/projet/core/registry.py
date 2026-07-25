from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional

from .backup import create_registry_backup
from .logger import log
from .models import ScriptEntry, utc_now
from .paths import REGISTRY_FILE, ensure_directories
from .settings import load_settings


@dataclass
class Registry:
    scripts: List[ScriptEntry] = field(default_factory=list)
    schema_version: int = 1

    @classmethod
    def load(cls) -> "Registry":
        ensure_directories()
        if not REGISTRY_FILE.exists():
            registry = cls()
            registry.save(create_backup=False)
            return registry
        try:
            data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            log(f"Registre illisible : {exc}", "ERROR")
            return cls()
        scripts = [ScriptEntry.from_dict(item) for item in data.get("scripts", []) if isinstance(item, dict)]
        return cls(scripts=scripts, schema_version=int(data.get("schema_version", 1)))

    def save(self, create_backup: bool = True) -> None:
        ensure_directories()
        settings = load_settings()
        if create_backup and settings.get("auto_backup_registry", True) and REGISTRY_FILE.exists():
            create_registry_backup()
        payload = {
            "schema_version": self.schema_version,
            "updated_at": utc_now(),
            "scripts": [entry.to_dict() for entry in self.scripts]
        }
        temp = REGISTRY_FILE.with_suffix(".tmp")
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(REGISTRY_FILE)
        log(f"Registre enregistré : {len(self.scripts)} script(s)")

    def add(self, entry: ScriptEntry) -> ScriptEntry:
        if self.get(entry.id):
            raise ValueError(f"Identifiant déjà présent : {entry.id}")
        self.scripts.append(entry)
        self.save()
        return entry

    def remove(self, script_id: str, delete_local_file: bool = True) -> ScriptEntry:
        entry = self.require(script_id)
        self.scripts = [item for item in self.scripts if item.id != script_id]
        self.save()
        if delete_local_file:
            try:
                Path(entry.local_path).unlink(missing_ok=True)
            except OSError as exc:
                log(f"Suppression locale impossible pour {entry.name}: {exc}", "WARNING")
        return entry

    def get(self, script_id: str) -> Optional[ScriptEntry]:
        return next((item for item in self.scripts if item.id == script_id), None)

    def require(self, script_id: str) -> ScriptEntry:
        entry = self.get(script_id)
        if entry is None:
            raise KeyError(f"Script inconnu : {script_id}")
        return entry

    def search(self, query: str = "") -> List[ScriptEntry]:
        needle = query.strip().lower()
        items: Iterable[ScriptEntry] = self.scripts
        if needle:
            items = [item for item in items if needle in item.name.lower() or needle in item.category.lower()]
        return sorted(items, key=lambda item: (not item.favorite, item.name.lower()))
