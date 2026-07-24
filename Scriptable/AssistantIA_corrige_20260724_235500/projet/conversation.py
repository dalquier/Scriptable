"""Gestion des conversations d'AssistantIA corrigé."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import uuid4

from storage import SQLiteStorage, StorageError


class ConversationManager:
    def __init__(self, storage: SQLiteStorage) -> None:
        self.storage = storage

    def create(self, title: str = "Nouvelle conversation") -> Dict[str, Any]:
        return self.storage.create_conversation(str(uuid4()), title)

    def ensure(self, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        if conversation_id:
            try:
                return self.storage.get_conversation(conversation_id)
            except StorageError:
                pass
        conversations = self.storage.list_conversations(limit=1)
        if conversations:
            return conversations[0]
        return self.create()

    def list(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.storage.list_conversations(limit)

    def messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        self.storage.get_conversation(conversation_id)
        return self.storage.list_messages(conversation_id)

    def add_user_message(self, conversation_id: str, content: str) -> Dict[str, Any]:
        return self.storage.add_message(conversation_id, "user", content)

    def add_assistant_message(self, conversation_id: str, content: str) -> Dict[str, Any]:
        return self.storage.add_message(conversation_id, "assistant", content)

    def rename(self, conversation_id: str, title: str) -> Dict[str, Any]:
        return self.storage.rename_conversation(conversation_id, title)

    def delete(self, conversation_id: str) -> None:
        self.storage.delete_conversation(conversation_id)

    def build_api_input(self, conversation_id: str) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for message in self.messages(conversation_id):
            role = str(message.get("role", "user"))
            if role not in {"user", "assistant", "developer", "system"}:
                continue
            text = str(message.get("content", "")).strip()
            if not text:
                continue
            result.append(
                {
                    "role": role,
                    "content": [
                        {
                            "type": "input_text",
                            "text": text,
                        }
                    ],
                }
            )
        return result

    @staticmethod
    def suggest_title(text: str) -> str:
        normalized = " ".join(text.strip().split())
        return normalized[:60] or "Nouvelle conversation"
