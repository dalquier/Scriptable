"""Gestion de la conversation active."""

from __future__ import annotations

from typing import Any, Dict, List

from storage import Storage


class ConversationManager:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.conversation_id = storage.get_latest_conversation_id()
        if self.conversation_id is None:
            self.conversation_id = storage.create_conversation()

    def new_conversation(self) -> int:
        self.conversation_id = self.storage.create_conversation()
        return self.conversation_id

    def add_user_message(self, content: str) -> None:
        self.storage.add_message(self.conversation_id, "user", content)
        messages = self.storage.get_messages(self.conversation_id)
        if len(messages) == 1:
            title = " ".join(content.strip().split())[:48]
            if title:
                self.storage.rename_conversation(self.conversation_id, title)

    def add_assistant_message(self, content: str) -> None:
        self.storage.add_message(self.conversation_id, "assistant", content)

    def messages(self) -> List[Dict[str, Any]]:
        return self.storage.get_messages(self.conversation_id)

    def api_input(self) -> List[Dict[str, Any]]:
        return [
            {"role": message["role"], "content": message["content"]}
            for message in self.messages()
            if message.get("role") in {"user", "assistant"}
        ]
