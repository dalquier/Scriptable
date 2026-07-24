"""Noyau applicatif d'AssistantIA corrigé."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from api_client import OpenAIClient
from config import (
    DATABASE_PATH,
    MAX_OUTPUT_TOKENS,
    OPENAI_API_URL,
    OPENAI_MODEL,
    REQUEST_TIMEOUT_SECONDS,
    SYSTEM_PROMPT,
    ensure_directories,
    load_openai_api_key,
)
from conversation import ConversationManager
from storage import SQLiteStorage


class AssistantIAApp:
    def __init__(self) -> None:
        ensure_directories()
        self.storage = SQLiteStorage(DATABASE_PATH)
        self.conversations = ConversationManager(self.storage)
        self.client = OpenAIClient(
            api_key=load_openai_api_key(),
            model=OPENAI_MODEL,
            api_url=OPENAI_API_URL,
            timeout_seconds=REQUEST_TIMEOUT_SECONDS,
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )
        self.current_conversation_id: Optional[str] = None

    def start(self, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        conversation = self.conversations.ensure(conversation_id)
        self.current_conversation_id = str(conversation["id"])
        return conversation

    def new_conversation(self, title: str = "Nouvelle conversation") -> Dict[str, Any]:
        conversation = self.conversations.create(title)
        self.current_conversation_id = str(conversation["id"])
        return conversation

    def list_conversations(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.conversations.list(limit)

    def get_messages(self, conversation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.conversations.messages(self._require_conversation(conversation_id))

    def delete_conversation(self, conversation_id: str) -> None:
        self.conversations.delete(conversation_id)
        if self.current_conversation_id == conversation_id:
            self.current_conversation_id = None

    def send_message(
        self,
        text: str,
        conversation_id: Optional[str] = None,
        enable_web_search: bool = False,
    ) -> str:
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("Le message ne peut pas être vide.")

        target = self._require_conversation(conversation_id)
        previous_messages = self.conversations.messages(target)
        self.conversations.add_user_message(target, clean_text)

        if not previous_messages:
            self.conversations.rename(target, self.conversations.suggest_title(clean_text))

        answer = self.client.ask(
            messages=self.conversations.build_api_input(target),
            instructions=SYSTEM_PROMPT,
            enable_web_search=enable_web_search,
            metadata={"app": "AssistantIA", "version": "corrigee"},
        )
        self.conversations.add_assistant_message(target, answer)
        return answer

    def _require_conversation(self, conversation_id: Optional[str]) -> str:
        target = conversation_id or self.current_conversation_id
        if target:
            return target
        return str(self.start()["id"])

    def close(self) -> None:
        self.storage.close()

    def __enter__(self) -> "AssistantIAApp":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()
