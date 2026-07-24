"""Persistance SQLite locale pour AssistantIA v5."""

from __future__ import annotations

import os
import sqlite3
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional


class Storage:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self._lock = threading.RLock()
        os.makedirs(os.path.dirname(database_path), exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._lock, self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                );
                """
            )

    @staticmethod
    def _now() -> str:
        return datetime.now().isoformat(timespec="seconds")

    def create_conversation(self, title: str = "Nouvelle conversation") -> int:
        now = self._now()
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO conversations(title, created_at, updated_at) VALUES (?, ?, ?)",
                (title, now, now),
            )
            return int(cursor.lastrowid)

    def add_message(self, conversation_id: int, role: str, content: str) -> int:
        now = self._now()
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO messages(conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, now),
            )
            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (now, conversation_id),
            )
            return int(cursor.lastrowid)

    def get_messages(self, conversation_id: int) -> List[Dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                "SELECT role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY id",
                (conversation_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_latest_conversation_id(self) -> Optional[int]:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT id FROM conversations ORDER BY updated_at DESC, id DESC LIMIT 1"
            ).fetchone()
        return int(row["id"]) if row else None
