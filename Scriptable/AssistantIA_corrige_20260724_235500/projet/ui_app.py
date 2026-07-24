"""Interface native Pyto compatible avec plusieurs versions de pyto_ui."""

from __future__ import annotations

import threading
from typing import Any, Dict, List

import pyto_ui as ui

from api_client import OpenAIClientError
from app import AssistantIAApp
from config import APP_NAME, APP_VERSION


def _system_color(name: str, fallback: Any = None) -> Any:
    colors = getattr(ui, "SystemColors", None)
    if colors is not None and hasattr(colors, name):
        return getattr(colors, name)
    legacy_name = f"COLOR_{name}"
    if hasattr(ui, legacy_name):
        return getattr(ui, legacy_name)
    return fallback


def _system_button() -> Any:
    button_type = getattr(ui, "ButtonType", None)
    if button_type is not None and hasattr(button_type, "SYSTEM"):
        return button_type.SYSTEM
    return getattr(ui, "BUTTON_TYPE_SYSTEM", None)


def _presentation_fullscreen() -> Any:
    mode = getattr(ui, "PresentationMode", None)
    if mode is not None and hasattr(mode, "FULLSCREEN"):
        return mode.FULLSCREEN
    return getattr(ui, "PRESENTATION_MODE_FULLSCREEN", "fullscreen")


def _make_button(title: str, action: Any) -> Any:
    button_type = _system_button()
    try:
        button = ui.Button(type=button_type, title=title)
    except Exception:
        try:
            button = ui.Button(title=title)
        except Exception:
            button = ui.Button()
            button.title = title
    button.action = action
    return button


class AssistantIAView(ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.title = APP_NAME
        self.background_color = _system_color("SYSTEM_BACKGROUND")
        self.app = AssistantIAApp()
        self.app.start()
        self.web_enabled = False
        self.is_sending = False
        self._build_ui()
        self.refresh_messages()

    def _build_ui(self) -> None:
        self.header = ui.View()
        self.header.background_color = _system_color("SECONDARY_SYSTEM_BACKGROUND")
        self.add_subview(self.header)

        self.title_label = ui.Label(text=f"{APP_NAME} {APP_VERSION}")
        self.title_label.text_color = _system_color("LABEL")
        self.header.add_subview(self.title_label)

        self.new_button = _make_button("Nouveau", self.new_conversation)
        self.header.add_subview(self.new_button)

        self.web_button = _make_button("Web : non", self.toggle_web)
        self.header.add_subview(self.web_button)

        self.transcript = ui.TextView(text="")
        self.transcript.editable = False
        self.transcript.background_color = _system_color("SYSTEM_BACKGROUND")
        self.transcript.text_color = _system_color("LABEL")
        self.add_subview(self.transcript)

        self.status = ui.Label(text="Prêt")
        self.status.text_color = _system_color("SECONDARY_LABEL")
        self.add_subview(self.status)

        self.composer = ui.View()
        self.composer.background_color = _system_color("SECONDARY_SYSTEM_BACKGROUND")
        self.add_subview(self.composer)

        self.input = ui.TextView(text="")
        self.input.background_color = _system_color("SYSTEM_BACKGROUND")
        self.input.text_color = _system_color("LABEL")
        self.composer.add_subview(self.input)

        self.send_button = _make_button("Envoyer", self.send_message)
        self.composer.add_subview(self.send_button)

    def layout(self) -> None:
        width = self.width
        height = self.height
        header_h = 72
        composer_h = 118
        status_h = 24
        bottom_margin = 8

        self.header.frame = (0, 0, width, header_h)
        self.title_label.frame = (16, 18, max(100, width - 220), 36)
        self.new_button.frame = (max(160, width - 190), 17, 82, 38)
        self.web_button.frame = (max(246, width - 104), 17, 94, 38)

        transcript_h = max(120, height - header_h - composer_h - status_h - bottom_margin)
        self.transcript.frame = (12, header_h + 4, width - 24, transcript_h - 4)
        self.status.frame = (16, header_h + transcript_h, width - 32, status_h)

        composer_y = height - composer_h - bottom_margin
        self.composer.frame = (0, composer_y, width, composer_h + bottom_margin)
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
            return "Bienvenue dans AssistantIA corrigé.\n\nPosez votre question ci-dessous."
        blocks: List[str] = []
        for message in messages:
            role = str(message.get("role", "message"))
            if role == "user":
                label = "VOUS"
            elif role == "assistant":
                label = "ASSISTANT"
            else:
                label = role.upper()
            content = str(message.get("content", "")).strip()
            if content:
                blocks.append(f"{label}\n{content}")
        return "\n\n────────────────────\n\n".join(blocks)

    def toggle_web(self, sender: Any) -> None:
        self.web_enabled = not self.web_enabled
        self.web_button.title = "Web : oui" if self.web_enabled else "Web : non"
        self.status.text = (
            "Recherche Web activée" if self.web_enabled else "Recherche Web désactivée"
        )

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
        text = str(self.input.text or "").strip()
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
            self.status.text_color = (
                _system_color("RED") if error else _system_color("SECONDARY_LABEL")
            )
            self.refresh_messages()

        delay = getattr(ui, "delay", None)
        if callable(delay):
            try:
                delay(finish, 0)
                return
            except Exception:
                pass
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
    view = AssistantIAView()
    mode = _presentation_fullscreen()
    try:
        view.present(mode)
    except TypeError:
        view.present(presentation_mode=mode)
    return view
