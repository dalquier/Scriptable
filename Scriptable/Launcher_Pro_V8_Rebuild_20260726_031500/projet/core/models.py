from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class LauncherItem:
    id: str
    kind: str
    name: str
    category: str = "Général"
    favorite: bool = False
    local_path: str = ""
    source_path: str = ""
    project_root: str = ""
    entry_script: str = ""
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    last_run_at: Optional[str] = None
    run_count: int = 0
    last_duration: Optional[float] = None
    last_status: str = "never"
    last_error: Optional[str] = None

    @classmethod
    def create_script(cls, name: str, local_path: str, source_path: str = "") -> "LauncherItem":
        return cls(id=uuid4().hex, kind="script", name=name.strip(), local_path=local_path, source_path=source_path)

    @classmethod
    def create_project(cls, name: str, project_root: str, entry_script: str) -> "LauncherItem":
        return cls(id=uuid4().hex, kind="project", name=name.strip(), project_root=project_root, entry_script=entry_script)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LauncherItem":
        allowed = cls.__dataclass_fields__.keys()
        return cls(**{key: value for key, value in data.items() if key in allowed})

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RunnerResult:
    success: bool
    duration: float
    output: str = ""
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
