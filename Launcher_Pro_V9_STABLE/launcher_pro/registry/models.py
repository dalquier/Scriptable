"""Domain models for registered launchable items."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4


class ItemKind(str, Enum):
    SCRIPT = "script"
    PROJECT = "project"


@dataclass(frozen=True)
class LibraryItem:
    id: str
    name: str
    kind: ItemKind
    source_path: str
    entrypoint: str
    favorite: bool = False
    created_at: str = ""

    @classmethod
    def create(cls, name: str, kind: ItemKind, source_path: Path, entrypoint: Path) -> "LibraryItem":
        return cls(
            id=str(uuid4()), name=name.strip(), kind=kind,
            source_path=str(source_path.resolve()), entrypoint=str(entrypoint.resolve()),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LibraryItem":
        return cls(
            id=str(data["id"]), name=str(data["name"]), kind=ItemKind(data["kind"]),
            source_path=str(data["source_path"]), entrypoint=str(data["entrypoint"]),
            favorite=bool(data.get("favorite", False)), created_at=str(data.get("created_at", "")),
        )
