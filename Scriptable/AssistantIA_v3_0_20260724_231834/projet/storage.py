"""Persistance SQLite des conversations et paramètres."""

from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class StorageError(RuntimeError):
    pass


class SQLiteStorage:
    def __init__(self, database_path: Path) -> None:
        self.database_path = str(database_path)
        self._lock = threading.RLock()
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    @contextmanager
    def _connection(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize_schema(self) -> None:
        with self._lock, self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                    ON messages(conversation_id, id);
                """
            )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_conversation(self, conversation_id: str, title: str) -> Dict[str, Any]:
        now = self._now()
        with self._lock, self._connection() as connection:
            connection.execute(
                "INSERT INTO conversations(id,title,created_at,updated_at) VALUES(?,?,?,?)",
                (conversation_id, title.strip() or "Nouvelle conversation", now, now),
            )
        return self.get_conversation(conversation_id)

    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        with self._lock, self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
            ).fetchone()
        if row is None:
            raise StorageError(f"Conversation introuvable : {conversation_id}")
        return dict(row)

    def list_conversations(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock, self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM conversations ORDER BY updated_at DESC LIMIT ?",
                (max(1, int(limit)),),
            ).fetchall()
        return [dict(row) for row in rows]

    def rename_conversation(self, conversation_id: str, title: str) -> Dict[str, Any]:
        with self._lock, self._connection() as connection:
            connection.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                (title.strip() or "Nouvelle conversation", self._now(), conversation_id),
            )
        return self.get_conversation(conversation_id)

    def delete_conversation(self, conversation_id: str) -> None:
        with self._lock, self._connection() as connection:
            connection.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))

    def add_message(self, conversation_id: str, role: str, content: str) -> Dict[str, Any]:
        if role not in {"system", "developer", "user", "assistant", "tool"}:
            raise StorageError(f"Rôle non pris en charge : {role}")
        now = self._now()
        with self._lock, self._connection() as connection:
            cursor = connection.execute(
                "INSERT INTO messages(conversation_id,role,content,created_at) VALUES(?,?,?,?)",
                (conversation_id, role, content, now),
            )
            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (now, conversation_id),
            )
            row = connection.execute(
                "SELECT * FROM messages WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return dict(row)

    def list_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        with self._lock, self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY id ASC",
                (conversation_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def set_setting(self, key: str, value: Any) -> None:
        payload = json.dumps(value, ensure_ascii=False)
        with self._lock, self._connection() as connection:
            connection.execute(
                """
                INSERT INTO settings(key,value_json,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json,
                updated_at=excluded.updated_at
                """,
                (key, payload, self._now()),
            )

    def get_setting(self, key: str, default: Optional[Any] = None) -> Any:
        with self._lock, self._connection() as connection:
            row = connection.execute(
                "SELECT value_json FROM settings WHERE key = ?", (key,)
            ).fetchone()
        if row is None:
            return default
        try:
            return json.loads(row["value_json"])
        except Exception:
            return default

    def close(self) -> None:
        return None
