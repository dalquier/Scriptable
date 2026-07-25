from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List
import uuid


@dataclass
class ScriptEntry:
    id: str
    name: str
    local_path: str
    source_path: str = ""
    favorite: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    last_run_at: str = ""
    run_count: int = 0
    last_status: str = "never"
    last_error: str = ""

    @classmethod
    def create(cls, name: str, local_path: str, source_path: str = "") -> "ScriptEntry":
        return cls(id=uuid.uuid4().hex, name=name.strip(), local_path=local_path, source_path=source_path)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScriptEntry":
        allowed = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in allowed})

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Registry:
    version: int = 1
    scripts: List[ScriptEntry] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Registry":
        return cls(version=int(data.get("version", 1)), scripts=[ScriptEntry.from_dict(x) for x in data.get("scripts", [])])

    def to_dict(self) -> Dict[str, Any]:
        return {"version": self.version, "scripts": [x.to_dict() for x in self.scripts]}

    def find(self, entry_id: str) -> ScriptEntry | None:
        return next((x for x in self.scripts if x.id == entry_id), None)
