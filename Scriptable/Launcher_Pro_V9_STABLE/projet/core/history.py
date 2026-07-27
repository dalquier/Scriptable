"""Journal métier JSON Lines de Launcher Pro V9."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any

from config import HISTORY_FILENAME
from .paths import DATA_DIR


@dataclass(frozen=True)
class HistoryEvent:
    """Événement métier persistant et sérialisable."""

    timestamp: str
    action: str
    success: bool
    item_id: str | None = None
    detail: str = ""


class HistoryJournal:
    """Journal append-only tolérant une dernière ligne incomplète."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path) if path is not None else DATA_DIR / HISTORY_FILENAME
        self._lock = RLock()

    def append(
        self,
        action: str,
        *,
        success: bool = True,
        item_id: str | None = None,
        detail: str = "",
    ) -> HistoryEvent:
        """Ajoute et synchronise un événement sur disque."""
        event = HistoryEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            action=action.strip() or "unknown",
            success=success,
            item_id=item_id,
            detail=detail,
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(asdict(event), ensure_ascii=False, separators=(",", ":"))
        with self._lock, self.path.open("a", encoding="utf-8") as stream:
            stream.write(line + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        return event

    def read(self, limit: int | None = None) -> list[HistoryEvent]:
        """Lit les événements valides, du plus ancien au plus récent."""
        if limit is not None and limit < 0:
            raise ValueError("La limite ne peut pas être négative")
        if not self.path.exists():
            return []
        events: list[HistoryEvent] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                payload: dict[str, Any] = json.loads(line)
                events.append(HistoryEvent(**payload))
            except (json.JSONDecodeError, TypeError):
                continue
        return events[-limit:] if limit else events
