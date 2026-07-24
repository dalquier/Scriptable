"""Noyau applicatif d'AssistantIA Studio.

Ce module orchestre la configuration, le stockage SQLite, les conversations et
le client OpenAI. Il ne dépend pas de l'interface graphique et peut donc être
utilisé depuis Pyto, une console Python ou de futurs écrans UI.
"""

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
    WEB_SEARCH_MODE,
    ensure_directories,
    load_openai_api_key,
)
from conversation import ConversationManager
from storage import SQLiteStorage


class AssistantIAApp:
    """Façade principale de l'application."""

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
        """Ouvre une conversation existante ou en crée une nouvelle."""

        conversation = self.conversations.ensure(conversation_id)
        self.current_conversation_id = str(conversation["id"])
        return conversation

    def new_conversation(self, title: str = "Nouvelle conversation") -> Dict[str, Any]:
        conversation = self.conversations.create(title)
        self.current_conversation_id = str(conversation["id"])
        return conversation

    def list_conversations(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.conversations.list(limit=limit)

    def get_messages(self, conversation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        target = self._require_conversation(conversation_id)
        return self.conversations.messages(target)

    def rename_current_conversation(self, title: str) -> Dict[str, Any]:
        target = self._require_conversation(None)
        return self.conversations.rename(target, title.strip() or "Nouvelle conversation")

    def delete_conversation(self, conversation_id: str) -> None:
        self.conversations.delete(conversation_id)
        if self.current_conversation_id == conversation_id:
            self.current_conversation_id = None

    def send_message(
        self,
        text: str,
        conversation_id: Optional[str] = None,
        enable_web_search: Optional[bool] = None,
    ) -> str:
        """Enregistre un message, appelle OpenAI puis persiste la réponse."""

        clean_text = text.strip()
        if not clean_text:
            raise ValueError("Le message ne peut pas être vide.")

        target = self._require_conversation(conversation_id)
        existing_messages = self.conversations.messages(target)
        self.conversations.add_user_message(target, clean_text)

        if not existing_messages:
            title = self.conversations.suggest_title(clean_text)
            self.conversations.rename(target, title)

        api_input = self.conversations.build_api_input(target)
        web_enabled = self._resolve_web_search(enable_web_search)

        answer = self.client.ask(
            messages=api_input,
            instructions=SYSTEM_PROMPT,
            enable_web_search=web_enabled,
        )
        self.conversations.add_assistant_message(target, answer)
        return answer

    def _require_conversation(self, conversation_id: Optional[str]) -> str:
        target = conversation_id or self.current_conversation_id
        if not target:
            conversation = self.start()
            target = str(conversation["id"])
        return target

    @staticmethod
    def _resolve_web_search(explicit: Optional[bool]) -> bool:
        if explicit is not None:
            return bool(explicit)

        mode = str(WEB_SEARCH_MODE).strip().lower()
        if mode == "always":
            return True
        if mode == "off":
            return False
        return False

    def close(self) -> None:
        close_method = getattr(self.storage, "close", None)
        if callable(close_method):
            close_method()

    def __enter__(self) -> "AssistantIAApp":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()
