"""Interface iPhone repensée pour AssistantIA v5."""

from __future__ import annotations

import threading
from typing import Any, Dict, List

import pyto_ui as ui

from api_client import OpenAIClientError
from app import AssistantIAApp
from config import APP_NAME, APP_VERSION


TOP_SAFE = 52
HEADER_HEIGHT = 58
COMPOSER_HEIGHT = 78
KEYBOARD_LIFT = 318
BOTTOM_SAFE = 18


def _color(name: str, fallback: Any = None) -> Any:
    colors = getattr(ui, "SystemColors", None)
    if colors is not None and hasattr(colors, name):
        return getattr(colors, name)
    legacy = f"COLOR_{name}"
    if hasattr(ui, legacy):
        return getattr(ui, legacy)
    return fallback


def _button(title: str, action: Any) -> Any:
    try:
        button = ui.Button(title=title)
    except Exception:
        button = ui.Button()
        button.title = title
    button.action = action
    return button


class InputDelegate:
    def __init__(self, owner: "AssistantIAView") -> None:
        self.owner = owner

    def text_view_did_begin_editing(self, text_view: Any) -> None:
        self.owner.keyboard_visible = True
        self.owner.layout()

    def text_view_did_end_editing(self, text_view: Any) -> None:
        self.owner.keyboard_visible = False
        self.owner.layout()

    def textview_did_begin_editing(self, text_view: Any) -> None:
        self.text_view_did_begin_editing(text_view)

    def textview_did_end_editing(self, text_view: Any) -> None:
        self.text_view_did_end_editing(text_view)


class AssistantIAView(ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.title = APP_NAME
        self.background_color = _color("SYSTEM_BACKGROUND")
        self.keyboard_visible = False
        self.web_enabled = False
        self.is_sending = False
        self.app = AssistantIAApp()
        self._build_ui()
        try:
            self.app.start()
            self.status.text = "Prêt"
        except Exception as exc:
            self.status.text = str(exc)
        self.refresh_messages()

    def _build_ui(self) -> None:
        self.header = ui.View()
        self.header.background_color = _color("SECONDARY_SYSTEM_BACKGROUND")
        self.add_subview(self.header)

        self.title_label = ui.Label(text=f"{APP_NAME}  v{APP_VERSION}")
        self.title_label.text_color = _color("LABEL")
        self.header.add_subview(self.title_label)

        self.new_button = _button("＋", self.new_conversation)
        self.header.add_subview(self.new_button)

        self.web_button = _button("Web off", self.toggle_web)
        self.header.add_subview(self.web_button)

        self.transcript = ui.TextView(text="")
        self.transcript.editable = False
        self.transcript.background_color = _color("SYSTEM_BACKGROUND")
        self.transcript.text_color = _color("LABEL")
        self.add_subview(self.transcript)

        self.status = ui.Label(text="Initialisation…")
        self.status.text_color = _color("SECONDARY_LABEL")
        self.add_subview(self.status)

        self.composer = ui.View()
        self.composer.background_color = _color("SECONDARY_SYSTEM_BACKGROUND")
        self.add_subview(self.composer)

        self.input = ui.TextView(text="")
        self.input.background_color = _color("TERTIARY_SYSTEM_BACKGROUND")
        self.input.text_color = _color("LABEL")
        self.input_delegate = InputDelegate(self)
        try:
            self.input.delegate = self.input_delegate
        except Exception:
            pass
        self.composer.add_subview(self.input)

        self.send_button = _button("Envoyer", self.send_message)
        self.composer.add_subview(self.send_button)

        self.hide_keyboard_button = _button("⌄", self.hide_keyboard)
        self.composer.add_subview(self.hide_keyboard_button)

    def layout(self) -> None:
        width = max(320, self.width)
        height = max(480, self.height)
        lift = KEYBOARD_LIFT if self.keyboard_visible else 0
        header_y = TOP_SAFE
        composer_y = height - COMPOSER_HEIGHT - BOTTOM_SAFE - lift

        self.header.frame = (0, header_y, width, HEADER_HEIGHT)
        self.title_label.frame = (16, 11, max(120, width - 190), 36)
        self.web_button.frame = (width - 132, 10, 78, 38)
        self.new_button.frame = (width - 48, 10, 38, 38)

        transcript_y = header_y + HEADER_HEIGHT
        status_h = 22
        transcript_h = max(120, composer_y - transcript_y - status_h)
        self.transcript.frame = (10, transcript_y + 4, width - 20, transcript_h - 4)
        self.status.frame = (16, transcript_y + transcript_h, width - 32, status_h)

        self.composer.frame = (0, composer_y, width, COMPOSER_HEIGHT + BOTTOM_SAFE)
        self.input.frame = (12, 10, max(120, width - 126), 56)
        self.send_button.frame = (width - 104, 10, 92, 56)
        self.hide_keyboard_button.frame = (width - 42, -34, 30, 30)
        self.hide_keyboard_button.hidden = not self.keyboard_visible

    def hide_keyboard(self, sender: Any) -> None:
        try:
            self.input.end_editing()
        except Exception:
            try:
                self.input.resign_first_responder()
            except Exception:
                pass
        self.keyboard_visible = False
        self.layout()

    def toggle_web(self, sender: Any) -> None:
        self.web_enabled = not self.web_enabled
        self.web_button.title = "Web on" if self.web_enabled else "Web off"
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
        text = str(self.input.text or "").strip()
        if not text:
            self.status.text = "Saisissez un message."
            return
        self.input.text = ""
        self.is_sending = True
        self.send_button.enabled = False
        self.new_button.enabled = False
        self.status.text = "AssistantIA réfléchit…"
        self.refresh_messages(extra_user=text)
        threading.Thread(target=self._send_worker, args=(text,), daemon=True).start()

    def _send_worker(self, text: str) -> None:
        error = None
        try:
            self.app.send_message(text, enable_web_search=self.web_enabled)
        except (OpenAIClientError, RuntimeError, ValueError) as exc:
            error = str(exc)
        except Exception as exc:
            error = f"Erreur inattendue : {exc}"

        def finish() -> None:
            self.is_sending = False
            self.send_button.enabled = True
            self.new_button.enabled = True
            self.status.text = error or "Prêt"
            self.refresh_messages()

        delay = getattr(ui, "delay", None)
        if callable(delay):
            try:
                delay(finish, 0)
                return
            except Exception:
                pass
        finish()

    def refresh_messages(self, extra_user: str | None = None) -> None:
        messages = list(self.app.get_messages())
        if extra_user:
            messages.append({"role": "user", "content": extra_user})
        self.transcript.text = self._format_messages(messages)
        try:
            self.transcript.scroll_range_to_visible(max(0, len(self.transcript.text) - 1), 1)
        except Exception:
            pass

    @staticmethod
    def _format_messages(messages: List[Dict[str, Any]]) -> str:
        if not messages:
            return "Bienvenue dans AssistantIA v5.\n\nÉcrivez votre message dans la barre située en bas de l’écran."
        blocks: List[str] = []
        for message in messages:
            role = message.get("role")
            label = "VOUS" if role == "user" else "ASSISTANT"
            content = str(message.get("content", "")).strip()
            if content:
                blocks.append(f"{label}\n{content}")
        return "\n\n────────────────────\n\n".join(blocks)


def present() -> AssistantIAView:
    view = AssistantIAView()
    mode = getattr(ui, "PRESENTATION_MODE_FULLSCREEN", "fullscreen")
    show_view = getattr(ui, "show_view", None)
    if callable(show_view):
        show_view(view, mode)
    else:
        raise RuntimeError("Cette version de Pyto ne fournit pas ui.show_view().")
    return view
