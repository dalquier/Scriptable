"""Interface graphique Pyto pour AssistantIA Studio.

Cette interface s'appuie uniquement sur ``pyto_ui`` et le noyau ``AssistantIAApp``.
Elle propose une conversation persistante, un champ de saisie toujours visible,
un bouton d'envoi, une nouvelle conversation et un interrupteur Web.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List

import pyto_ui as ui

from app import AssistantIAApp
from api_client import OpenAIClientError
from config import APP_NAME, APP_VERSION


BG = ui.COLOR_SYSTEM_BACKGROUND
PANEL = ui.COLOR_SECONDARY_SYSTEM_BACKGROUND
TEXT = ui.COLOR_LABEL
SECONDARY = ui.COLOR_SECONDARY_LABEL
ACCENT = ui.COLOR_SYSTEM_BLUE
DANGER = ui.COLOR_SYSTEM_RED


class AssistantIAView(ui.View):
    """Vue principale de l'application."""

    def __init__(self) -> None:
        super().__init__()
        self.title = APP_NAME
        self.background_color = BG
        self.app = AssistantIAApp()
        self.app.start()
        self.web_enabled = False
        self.is_sending = False
        self._build_ui()
        self.refresh_messages()

    def _build_ui(self) -> None:
        self.header = ui.View()
        self.header.background_color = PANEL
        self.add_subview(self.header)

        self.title_label = ui.Label()
        self.title_label.text = APP_NAME
        self.title_label.text_color = TEXT
        self.title_label.font = ui.Font.bold_system_font_of_size(20)
        self.header.add_subview(self.title_label)

        self.subtitle_label = ui.Label()
        self.subtitle_label.text = f"Version {APP_VERSION}"
        self.subtitle_label.text_color = SECONDARY
        self.subtitle_label.font = ui.Font.system_font_of_size(12)
        self.header.add_subview(self.subtitle_label)

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
        self.transcript.background_color = BG
        self.transcript.text_color = TEXT
        self.transcript.font = ui.Font.system_font_of_size(16)
        self.add_subview(self.transcript)

        self.status_label = ui.Label()
        self.status_label.text = "Prêt"
        self.status_label.text_color = SECONDARY
        self.status_label.font = ui.Font.system_font_of_size(12)
        self.add_subview(self.status_label)

        self.composer = ui.View()
        self.composer.background_color = PANEL
        self.add_subview(self.composer)

        self.input = ui.TextView()
        self.input.background_color = BG
        self.input.text_color = TEXT
        self.input.font = ui.Font.system_font_of_size(16)
        self.input.text = ""
        self.composer.add_subview(self.input)

        self.send_button = ui.Button(type=ui.BUTTON_TYPE_SYSTEM)
        self.send_button.title = "Envoyer"
        self.send_button.action = self.send_message
        self.composer.add_subview(self.send_button)

    def layout(self) -> None:
        width = self.width
        height = self.height
        safe_bottom = 8
        header_h = 74
        composer_h = 118
        status_h = 24

        self.header.frame = (0, 0, width, header_h)
        self.title_label.frame = (16, 10, max(100, width - 220), 28)
        self.subtitle_label.frame = (16, 39, 140, 20)
        self.new_button.frame = (max(160, width - 190), 18, 82, 38)
        self.web_button.frame = (max(246, width - 104), 18, 94, 38)

        transcript_h = max(100, height - header_h - composer_h - status_h - safe_bottom)
        self.transcript.frame = (12, header_h + 6, width - 24, transcript_h - 6)
        self.status_label.frame = (16, header_h + transcript_h, width - 32, status_h)

        composer_y = height - composer_h - safe_bottom
        self.composer.frame = (0, composer_y, width, composer_h + safe_bottom)
        self.input.frame = (12, 10, max(120, width - 112), composer_h - 20)
        self.send_button.frame = (width - 92, 10, 80, composer_h - 20)

    def refresh_messages(self) -> None:
        messages = self.app.get_messages()
        self.transcript.text = self._format_messages(messages)
        self._scroll_to_bottom()

    @staticmethod
    def _format_messages(messages: List[Dict[str, Any]]) -> str:
        if not messages:
            return (
                "Bienvenue dans AssistantIA Studio.\n\n"
                "Posez une question dans le champ ci-dessous. Vous pouvez activer "
                "la recherche Web avec le bouton en haut de l'écran."
            )

        blocks: List[str] = []
        for message in messages:
            role = str(message.get("role", "")).lower()
            content = str(message.get("content", "")).strip()
            if not content:
                continue
            if role == "user":
                label = "VOUS"
            elif role == "assistant":
                label = "ASSISTANT"
            elif role == "system":
                label = "SYSTÈME"
            else:
                label = role.upper() or "MESSAGE"
            blocks.append(f"{label}\n{content}")
        return "\n\n────────────────────\n\n".join(blocks)

    def _scroll_to_bottom(self) -> None:
        try:
            self.transcript.scroll_range_to_visible(
                max(0, len(self.transcript.text) - 1), 1
            )
        except Exception:
            pass

    def toggle_web(self, sender: Any) -> None:
        self.web_enabled = not self.web_enabled
        self.web_button.title = "Web : oui" if self.web_enabled else "Web : non"
        self.status_label.text = (
            "Recherche Web activée" if self.web_enabled else "Recherche Web désactivée"
        )

    def new_conversation(self, sender: Any) -> None:
        if self.is_sending:
            return
        self.app.new_conversation()
        self.input.text = ""
        self.status_label.text = "Nouvelle conversation"
        self.refresh_messages()

    def send_message(self, sender: Any) -> None:
        if self.is_sending:
            return
        text = self.input.text.strip()
        if not text:
            self.status_label.text = "Saisissez un message."
            return

        self.input.text = ""
        self.is_sending = True
        self.send_button.enabled = False
        self.new_button.enabled = False
        self.status_label.text = "Réponse en cours…"

        # Le message utilisateur est ajouté par le noyau. On affiche une version
        # provisoire immédiatement afin que l'interface paraisse réactive.
        previous = self.transcript.text.strip()
        provisional = f"VOUS\n{text}\n\n────────────────────\n\nASSISTANT\n…"
        self.transcript.text = f"{previous}\n\n{provisional}" if previous else provisional
        self._scroll_to_bottom()

        thread = threading.Thread(
            target=self._send_worker,
            args=(text,),
            daemon=True,
        )
        thread.start()

    def _send_worker(self, text: str) -> None:
        try:
            self.app.send_message(text, enable_web_search=self.web_enabled)
            error = None
        except (OpenAIClientError, ValueError, RuntimeError) as exc:
            error = str(exc)
        except Exception as exc:  # Dernier filet de sécurité pour l'interface.
            error = f"Erreur inattendue : {exc}"

        def finish() -> None:
            self.is_sending = False
            self.send_button.enabled = True
            self.new_button.enabled = True
            if error:
                self.status_label.text = error
                self.status_label.text_color = DANGER
            else:
                self.status_label.text = "Prêt"
                self.status_label.text_color = SECONDARY
            self.refresh_messages()

        try:
            ui.delay(finish, 0)
        except Exception:
            finish()

    def close(self) -> None:
        try:
            self.app.close()
        finally:
            try:
                super().close()
            except Exception:
                pass


def present() -> AssistantIAView:
    """Crée et affiche l'interface dans Pyto."""

    view = AssistantIAView()
    view.present("fullscreen")
    return view
