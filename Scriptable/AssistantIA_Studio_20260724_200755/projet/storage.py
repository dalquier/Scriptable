"""Persistance SQLite pour AssistantIA Studio."""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


class StorageError(RuntimeError):
    """Erreur de persistance lisible par l'application."""


class SQLiteStorage:
    """Stockage local des conversations, messages et paramètres."""

    def __init__(self, database_path: str) -> None:
        self.database_path = os.path.abspath(database_path)
        self._lock = threading.RLock()
        self._ensure_parent_directory()
        self._initialize_schema()

    def _ensure_parent_directory(self) -> None:
        parent = os.path.dirname(self.database_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

    @contextmanager
    def _connection(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
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
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    FOREIGN KEY (conversation_id)
                        REFERENCES conversations(id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                    ON messages(conversation_id, id);
                CREATE INDEX IF NOT EXISTS idx_conversations_updated
                    ON conversations(updated_at DESC);
                """
            )

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _json_dump(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def _json_load(value: Optional[str], default: Any) -> Any:
        if not value:
            return default
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return default

    def create_conversation(
        self,
        conversation_id: str,
        title: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        now = self._utc_now()
        with self._lock, self._connection() as connection:
            connection.execute(
                """
                INSERT INTO conversations (
                    id, title, created_at, updated_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    title.strip() or "Nouvelle conversation",
                    now,
                    now,
                    self._json_dump(metadata or {}),
                ),
            )
        return self.get_conversation(conversation_id)

    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        with self._lock, self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()
        if row is None:
            raise StorageError(f"Conversation introuvable : {conversation_id}")
        return self._conversation_from_row(row)

    def list_conversations(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock, self._connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM conversations
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (max(1, int(limit)),),
            ).fetchall()
        return [self._conversation_from_row(row) for row in rows]

    def update_conversation(
        self,
        conversation_id: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        current = self.get_conversation(conversation_id)
        next_title = current["title"] if title is None else (title.strip() or current["title"])
        next_metadata = current["metadata"] if metadata is None else metadata
        with self._lock, self._connection() as connection:
            connection.execute(
                """
                UPDATE conversations
                SET title = ?, metadata_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    next_title,
                    self._json_dump(next_metadata),
                    self._utc_now(),
                    conversation_id,
                ),
            )
        return self.get_conversation(conversation_id)

    def delete_conversation(self, conversation_id: str) -> None:
        with self._lock, self._connection() as connection:
            connection.execute(
                "DELETE FROM conversations WHERE id = ?",
                (conversation_id,),
            )

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        role = role.strip().lower()
        if role not in {"system", "user", "assistant", "developer", "tool"}:
            raise StorageError(f"Rôle de message non pris en charge : {role}")
        now = self._utc_now()
        with self._lock, self._connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO messages (
                    conversation_id, role, content, created_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    role,
                    content,
                    now,
                    self._json_dump(metadata or {}),
                ),
            )
            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (now, conversation_id),
            )
            message_id = cursor.lastrowid
            row = connection.execute(
                "SELECT * FROM messages WHERE id = ?",
                (message_id,),
            ).fetchone()
        return self._message_from_row(row)

    def list_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        with self._lock, self._connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY id ASC
                """,
                (conversation_id,),
            ).fetchall()
        return [self._message_from_row(row) for row in rows]

    def replace_messages(
        self,
        conversation_id: str,
        messages: Iterable[Dict[str, Any]],
    ) -> None:
        with self._lock, self._connection() as connection:
            connection.execute(
                "DELETE FROM messages WHERE conversation_id = ?",
                (conversation_id,),
            )
            for message in messages:
                connection.execute(
                    """
                    INSERT INTO messages (
                        conversation_id, role, content, created_at, metadata_json
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        conversation_id,
                        str(message.get("role", "user")),
                        str(message.get("content", "")),
                        str(message.get("created_at") or self._utc_now()),
                        self._json_dump(message.get("metadata") or {}),
                    ),
                )
            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (self._utc_now(), conversation_id),
            )

    def set_setting(self, key: str, value: Any) -> None:
        now = self._utc_now()
        with self._lock, self._connection() as connection:
            connection.execute(
                """
                INSERT INTO settings (key, value_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value_json = excluded.value_json,
                    updated_at = excluded.updated_at
                """,
                (key, self._json_dump(value), now),
            )

    def get_setting(self, key: str, default: Any = None) -> Any:
        with self._lock, self._connection() as connection:
            row = connection.execute(
                "SELECT value_json FROM settings WHERE key = ?",
                (key,),
            ).fetchone()
        if row is None:
            return default
        return self._json_load(row["value_json"], default)

    def _conversation_from_row(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "title": row["title"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "metadata": self._json_load(row["metadata_json"], {}),
        }

    def _message_from_row(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "conversation_id": row["conversation_id"],
            "role": row["role"],
            "content": row["content"],
            "created_at": row["created_at"],
            "metadata": self._json_load(row["metadata_json"], {}),
        }
