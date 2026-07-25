from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class ScriptEntry:
    id: str
    name: str
    local_path: str
    source_path: str = ""
    category: str = "Général"
    favorite: bool = False
    icon: str = "terminal"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    last_run_at: Optional[str] = None
    run_count: int = 0
    last_duration: Optional[float] = None
    last_status: str = "never"
    last_error: Optional[str] = None

    @classmethod
    def create(cls, name: str, local_path: str, source_path: str = "") -> "ScriptEntry":
        return cls(id=uuid4().hex, name=name.strip(), local_path=local_path, source_path=source_path)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScriptEntry":
        allowed = cls.__dataclass_fields__.keys()
        return cls(**{key: value for key, value in data.items() if key in allowed})

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RunnerResult:
    success: bool
    duration: float
    error: Optional[str] = None
    output: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
