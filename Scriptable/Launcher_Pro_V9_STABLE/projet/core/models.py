"""Modèles de données sérialisables de Launcher Pro V9."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

VALID_KINDS = {"script", "project"}
VALID_STATUSES = {"never", "success", "error"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class LauncherItem:
    """Un script autonome ou un projet enregistré dans la bibliothèque."""

    id: str
    kind: str
    name: str
    local_path: str
    entry_script: str = ""
    source_path: str = ""
    category: str = "Sans catégorie"
    favorite: bool = False
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    run_count: int = 0
    last_status: str = "never"
    last_run_at: str | None = None
    last_duration: float | None = None
    last_error: str | None = None

    def __post_init__(self) -> None:
        self.validate()

    @classmethod
    def create_script(cls, name: str, local_path: str, source_path: str = "") -> "LauncherItem":
        return cls(
            id=uuid4().hex,
            kind="script",
            name=name.strip(),
            local_path=local_path,
            source_path=source_path,
        )

    @classmethod
    def create_project(
        cls,
        name: str,
        local_path: str,
        entry_script: str,
        source_path: str = "",
    ) -> "LauncherItem":
        return cls(
            id=uuid4().hex,
            kind="project",
            name=name.strip(),
            local_path=local_path,
            entry_script=entry_script,
            source_path=source_path,
        )

    def validate(self) -> None:
        if not self.id:
            raise ValueError("Identifiant d'élément manquant")
        if self.kind not in VALID_KINDS:
            raise ValueError(f"Type d'élément invalide : {self.kind}")
        if not self.name.strip():
            raise ValueError("Le nom ne peut pas être vide")
        if not self.local_path:
            raise ValueError("Le chemin local ne peut pas être vide")
        if self.kind == "project" and not self.entry_script:
            raise ValueError("Un projet doit posséder un fichier de lancement")
        if self.last_status not in VALID_STATUSES:
            raise ValueError(f"Statut invalide : {self.last_status}")
        if self.run_count < 0:
            raise ValueError("Le compteur de lancements ne peut pas être négatif")

    def touch(self) -> None:
        self.updated_at = utc_now()

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LauncherItem":
        return cls(**data)
