"""Noyau applicatif AssistantAI new, indépendant de pyto_ui."""

import os
import threading
from typing import Any, Dict, List, Optional

from api_client import OpenAIClient
from conversation import ConversationManager
from storage import Storage


class AssistantIAApp:
    def __init__(self, storage: Optional[Storage] = None, client: Any = None) -> None:
        root = os.path.dirname(os.path.abspath(__file__))
        self.storage = storage or Storage(os.path.join(root, "database", "assistantai_new.sqlite3"))
        self.conversations = ConversationManager(self.storage)
        self.client = client
        self._send_lock = threading.Lock()

    def start(self) -> None:
        if self.client is None:
            self.client = OpenAIClient()

    def new_conversation(self) -> int:
        return self.conversations.new_conversation()

    def get_messages(self) -> List[Dict[str, Any]]:
        return self.conversations.messages()

    def send_message(self, text: str, enable_web_search: bool = False) -> Dict[str, Any]:
        clean = (text or "").strip()
        if not clean:
            raise ValueError("Le message est vide.")
        if not self._send_lock.acquire(False):
            raise RuntimeError("Une réponse est déjà en cours.")
        try:
            self.conversations.add_user_message(clean)
            self.start()
            result = self.client.create_response(
                self.conversations.api_input(),
                enable_web_search=enable_web_search,
            )
            if isinstance(result, str):
                result = {"text": result, "sources": [], "metadata": {}}
            self.conversations.add_assistant_message(result["text"])
            result["web_used"] = bool(enable_web_search)
            return result
        finally:
            self._send_lock.release()

    def close(self) -> None:
        self.storage.close()
