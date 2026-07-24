"""Gestion métier des conversations."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from storage import SQLiteStorage


class ConversationManager:
    def __init__(self, storage: SQLiteStorage) -> None:
        self.storage = storage

    def create(self, title: str = "Nouvelle conversation") -> Dict[str, Any]:
        return self.storage.create_conversation(str(uuid.uuid4()), title)

    def ensure(self, conversation_id: Optional[str]) -> Dict[str, Any]:
        if conversation_id:
            try:
                return self.storage.get_conversation(conversation_id)
            except Exception:
                pass
        return self.create()

    def rename(self, conversation_id: str, title: str) -> Dict[str, Any]:
        return self.storage.rename_conversation(conversation_id, title)

    def delete(self, conversation_id: str) -> None:
        self.storage.delete_conversation(conversation_id)

    def list(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.storage.list_conversations(limit)

    def messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        return self.storage.list_messages(conversation_id)

    def add_user_message(self, conversation_id: str, content: str) -> Dict[str, Any]:
        return self.storage.add_message(conversation_id, "user", content)

    def add_assistant_message(self, conversation_id: str, content: str) -> Dict[str, Any]:
        return self.storage.add_message(conversation_id, "assistant", content)

    def build_api_input(self, conversation_id: str) -> List[Dict[str, str]]:
        result: List[Dict[str, str]] = []
        for message in self.messages(conversation_id):
            role = str(message.get("role", ""))
            if role in {"system", "developer", "user", "assistant"}:
                result.append({"role": role, "content": str(message.get("content", ""))})
        return result

    @staticmethod
    def suggest_title(text: str, max_length: int = 50) -> str:
        compact = " ".join(text.strip().split())
        if not compact:
            return "Nouvelle conversation"
        return compact if len(compact) <= max_length else compact[: max_length - 1].rstrip() + "…"
