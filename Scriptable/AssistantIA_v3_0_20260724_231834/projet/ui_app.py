"""Interface graphique native Pyto d'AssistantIA v3.0."""

from __future__ import annotations

import threading
from typing import Any, Dict, List

import pyto_ui as ui

from api_client import OpenAIClientError
from app import AssistantIAApp
from config import APP_NAME, APP_VERSION


class AssistantIAView(ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.title = APP_NAME
        self.background_color = ui.COLOR_SYSTEM_BACKGROUND
        self.app = AssistantIAApp()
        self.app.start()
        self.web_enabled = False
        self.is_sending = False
        self._build_ui()
        self.refresh_messages()

    def _build_ui(self) -> None:
        self.header = ui.View()
        self.header.background_color = ui.COLOR_SECONDARY_SYSTEM_BACKGROUND
        self.add_subview(self.header)

        self.title_label = ui.Label()
        self.title_label.text = f"{APP_NAME} {APP_VERSION}"
        self.title_label.font = ui.Font.bold_system_font_of_size(20)
        self.header.add_subview(self.title_label)

        self.new_button = ui.Button(type=ui.BUTTON_TYPE_SYSTEM)
        self.new_button.title = "Nouveau"
        self.new_button.action = self.new_conversation
        self.header.add_subview(self.new_button)

        self.web_button = ui.Button(type=ui.BUTTON_TYPE_SYSTEM)
        self.web_button.title = "Web : non"
        self.web_button.action = self.toggle_web
        self.header.add_subview(self.web_button)

        self.transcript = ui.TextView()
        self.transcript.editable = False
        self.transcript.background_color = ui.COLOR_SYSTEM_BACKGROUND
        self.transcript.font = ui.Font.system_font_of_size(16)
        self.add_subview(self.transcript)

        self.status = ui.Label()
        self.status.text = "Prêt"
        self.status.font = ui.Font.system_font_of_size(12)
        self.status.text_color = ui.COLOR_SECONDARY_LABEL
        self.add_subview(self.status)

        self.composer = ui.View()
        self.composer.background_color = ui.COLOR_SECONDARY_SYSTEM_BACKGROUND
        self.add_subview(self.composer)

        self.input = ui.TextView()
        self.input.font = ui.Font.system_font_of_size(16)
        self.input.background_color = ui.COLOR_SYSTEM_BACKGROUND
        self.composer.add_subview(self.input)

        self.send_button = ui.Button(type=ui.BUTTON_TYPE_SYSTEM)
        self.send_button.title = "Envoyer"
        self.send_button.action = self.send_message
        self.composer.add_subview(self.send_button)

    def layout(self) -> None:
        width, height = self.width, self.height
        header_h, composer_h, status_h = 72, 112, 24
        self.header.frame = (0, 0, width, header_h)
        self.title_label.frame = (16, 20, max(100, width - 220), 32)
        self.new_button.frame = (max(160, width - 190), 17, 82, 38)
        self.web_button.frame = (max(246, width - 104), 17, 94, 38)
        transcript_h = max(100, height - header_h - composer_h - status_h - 8)
        self.transcript.frame = (12, header_h + 4, width - 24, transcript_h - 4)
        self.status.frame = (16, header_h + transcript_h, width - 32, status_h)
        composer_y = height - composer_h - 8
        self.composer.frame = (0, composer_y, width, composer_h + 8)
        self.input.frame = (12, 10, max(120, width - 112), composer_h - 20)
        self.send_button.frame = (width - 92, 10, 80, composer_h - 20)

    def refresh_messages(self) -> None:
        self.transcript.text = self._format_messages(self.app.get_messages())
        try:
            self.transcript.scroll_range_to_visible(max(0, len(self.transcript.text) - 1), 1)
        except Exception:
            pass

    @staticmethod
    def _format_messages(messages: List[Dict[str, Any]]) -> str:
        if not messages:
            return "Bienvenue dans AssistantIA v3.0.\n\nPosez votre question ci-dessous."
        blocks: List[str] = []
        for message in messages:
            role = str(message.get("role", "message"))
            label = "VOUS" if role == "user" else "ASSISTANT" if role == "assistant" else role.upper()
            content = str(message.get("content", "")).strip()
            if content:
                blocks.append(f"{label}\n{content}")
        return "\n\n────────────────────\n\n".join(blocks)

    def toggle_web(self, sender: Any) -> None:
        self.web_enabled = not self.web_enabled
        self.web_button.title = "Web : oui" if self.web_enabled else "Web : non"
        self.status.text = "Recherche Web activée" if self.web_enabled else "Recherche Web désactivée"

    def new_conversation(self, sender: Any) -> None:
        if self.is_sending:
            return
        self.app.new_conversation()
        self.input.text = ""
        self.status.text = "Nouvelle conversation"
        self.refresh_messages()

    def send_message(self, sender: Any) -> None:
        if self.is_sending:
            return
        text = self.input.text.strip()
        if not text:
            self.status.text = "Saisissez un message."
            return
        self.input.text = ""
        self.is_sending = True
        self.send_button.enabled = False
        self.new_button.enabled = False
        self.status.text = "Réponse en cours…"
        threading.Thread(target=self._send_worker, args=(text,), daemon=True).start()

    def _send_worker(self, text: str) -> None:
        try:
            self.app.send_message(text, enable_web_search=self.web_enabled)
            error = None
        except (OpenAIClientError, RuntimeError, ValueError) as exc:
            error = str(exc)
        except Exception as exc:
            error = f"Erreur inattendue : {exc}"

        def finish() -> None:
            self.is_sending = False
            self.send_button.enabled = True
            self.new_button.enabled = True
            self.status.text = error or "Prêt"
            self.status.text_color = ui.COLOR_SYSTEM_RED if error else ui.COLOR_SECONDARY_LABEL
            self.refresh_messages()

        try:
            ui.delay(finish, 0)
        except Exception:
            finish()

    def close(self) -> None:
        self.app.close()
        try:
            super().close()
        except Exception:
            pass


def present() -> AssistantIAView:
    view = AssistantIAView()
    view.present("fullscreen")
    return view
