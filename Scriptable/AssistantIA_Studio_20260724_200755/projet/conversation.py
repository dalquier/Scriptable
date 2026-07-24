"""Gestion métier des conversations d'AssistantIA Studio."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from storage import SQLiteStorage


class ConversationManager:
    """Coordonne les conversations et leur persistance."""

    def __init__(self, storage: SQLiteStorage) -> None:
        self.storage = storage

    def create(self, title: str = "Nouvelle conversation") -> Dict[str, Any]:
        conversation_id = str(uuid.uuid4())
        return self.storage.create_conversation(conversation_id, title)

    def ensure(self, conversation_id: Optional[str]) -> Dict[str, Any]:
        if conversation_id:
            try:
                return self.storage.get_conversation(conversation_id)
            except Exception:
                pass
        return self.create()

    def rename(self, conversation_id: str, title: str) -> Dict[str, Any]:
        return self.storage.update_conversation(conversation_id, title=title)

    def delete(self, conversation_id: str) -> None:
        self.storage.delete_conversation(conversation_id)

    def list(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.storage.list_conversations(limit=limit)

    def messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        return self.storage.list_messages(conversation_id)

    def add_user_message(self, conversation_id: str, content: str) -> Dict[str, Any]:
        return self.storage.add_message(conversation_id, "user", content)

    def add_assistant_message(self, conversation_id: str, content: str) -> Dict[str, Any]:
        return self.storage.add_message(conversation_id, "assistant", content)

    def add_system_message(self, conversation_id: str, content: str) -> Dict[str, Any]:
        return self.storage.add_message(conversation_id, "system", content)

    def build_api_input(self, conversation_id: str) -> List[Dict[str, str]]:
        result: List[Dict[str, str]] = []
        for message in self.messages(conversation_id):
            role = message["role"]
            if role not in {"system", "user", "assistant", "developer"}:
                continue
            result.append({"role": role, "content": message["content"]})
        return result

    def suggest_title(self, user_text: str, max_length: int = 50) -> str:
        compact = " ".join(user_text.strip().split())
        if not compact:
            return "Nouvelle conversation"
        if len(compact) <= max_length:
            return compact
        return compact[: max_length - 1].rstrip() + "…"
