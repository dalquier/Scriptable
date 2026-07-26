"""Persistance SQLite locale, transactionnelle et utilisable entre threads."""

import os
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class StorageError(RuntimeError):
    pass


class Storage:
    VALID_ROLES = ("user", "assistant")

    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self._lock = threading.RLock()
        directory = os.path.dirname(os.path.abspath(database_path))
        os.makedirs(directory, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=15)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 15000")
        return connection

    def _initialize(self) -> None:
        with self._lock, self._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user','assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
                    ON messages(conversation_id, id);
            """)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")

    def create_conversation(self, title: str = "Nouvelle conversation") -> int:
        clean = (title or "").strip() or "Nouvelle conversation"
        now = self._now()
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO conversations(title, created_at, updated_at) VALUES (?, ?, ?)",
                (clean, now, now),
            )
            return int(cursor.lastrowid)

    def add_message(self, conversation_id: int, role: str, content: str) -> int:
        if role not in self.VALID_ROLES:
            raise ValueError("Rôle de message invalide.")
        clean = (content or "").strip()
        if not clean:
            raise ValueError("Le contenu du message est vide.")
        now = self._now()
        try:
            with self._lock, self._connect() as connection:
                cursor = connection.execute(
                    "INSERT INTO messages(conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                    (conversation_id, role, clean, now),
                )
                updated = connection.execute(
                    "UPDATE conversations SET updated_at = ? WHERE id = ?",
                    (now, conversation_id),
                )
                if updated.rowcount != 1:
                    raise ValueError("Conversation introuvable.")
                return int(cursor.lastrowid)
        except sqlite3.Error as exc:
            raise StorageError("Impossible d'enregistrer le message.") from exc

    def get_messages(self, conversation_id: int) -> List[Dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                "SELECT id, role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY id ASC",
                (conversation_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_conversation(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()
        return dict(row) if row else None

    def list_conversations(self) -> List[Dict[str, Any]]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM conversations ORDER BY updated_at DESC, id DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def get_latest_conversation_id(self) -> Optional[int]:
        rows = self.list_conversations()
        return int(rows[0]["id"]) if rows else None

    def rename_conversation(self, conversation_id: int, title: str) -> None:
        clean = (title or "").strip()
        if not clean:
            raise ValueError("Le titre est vide.")
        with self._lock, self._connect() as connection:
            updated = connection.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                (clean, self._now(), conversation_id),
            )
            if updated.rowcount != 1:
                raise ValueError("Conversation introuvable.")

    def delete_conversation(self, conversation_id: int) -> None:
        with self._lock, self._connect() as connection:
            connection.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))

    def close(self) -> None:
        """Aucune connexion persistante : arrêt uniforme de l'application."""
