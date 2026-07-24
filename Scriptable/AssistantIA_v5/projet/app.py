"""Noyau applicatif AssistantIA v5."""

from __future__ import annotations

import os
from typing import Any, Dict, List

from api_client import OpenAIClient
from conversation import ConversationManager
from storage import Storage


class AssistantIAApp:
    def __init__(self) -> None:
        root = os.path.dirname(os.path.abspath(__file__))
        database_path = os.path.join(root, "database", "assistantia_v5.sqlite3")
        self.storage = Storage(database_path)
        self.conversations = ConversationManager(self.storage)
        self.client: OpenAIClient | None = None

    def start(self) -> None:
        if self.client is None:
            self.client = OpenAIClient()

    def new_conversation(self) -> int:
        return self.conversations.new_conversation()

    def get_messages(self) -> List[Dict[str, Any]]:
        return self.conversations.messages()

    def send_message(self, text: str, enable_web_search: bool = False) -> str:
        clean = text.strip()
        if not clean:
            raise ValueError("Le message est vide.")
        if self.client is None:
            self.start()
        self.conversations.add_user_message(clean)
        answer = self.client.create_response(
            self.conversations.api_input(),
            enable_web_search=enable_web_search,
        )
        self.conversations.add_assistant_message(answer)
        return answer

    def close(self) -> None:
        pass
