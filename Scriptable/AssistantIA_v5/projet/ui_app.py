"""Interface iPhone robuste pour AssistantIA v5.

Cette version évite de placer la saisie derrière le clavier :
la saisie s'effectue dans un panneau dédié situé dans la partie haute de l'écran.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List

import pyto_ui as ui

from api_client import OpenAIClientError
from app import AssistantIAApp
from config import APP_NAME, APP_VERSION


TOP_SAFE = 54
HEADER_HEIGHT = 58
BOTTOM_BAR_HEIGHT = 72
STATUS_HEIGHT = 22


def _color(name: str, fallback: Any = None) -> Any:
    colors = getattr(ui, "SystemColors", None)
    if colors is not None and hasattr(colors, name):
        return getattr(colors, name)
    legacy = f"COLOR_{name}"
    if hasattr(ui, legacy):
        return getattr(ui, legacy)
    return fallback


def _button(title: str, action: Any) -> Any:
    button_type = getattr(ui, "BUTTON_TYPE_SYSTEM", None)
    try:
        if button_type is not None:
            button = ui.Button(type=button_type, title=title)
        else:
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
        self.background_color = _color("SYSTEM_BACKGROUND")
        self.web_enabled = False
        self.is_sending = False
        self.composer_open = False
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

        self.new_button = _button("Nouveau", self.new_conversation)
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

        self.bottom_bar = ui.View()
        self.bottom_bar.background_color = _color("SECONDARY_SYSTEM_BACKGROUND")
        self.add_subview(self.bottom_bar)

        self.write_button = _button("Écrire un message…", self.open_composer)
        self.bottom_bar.add_subview(self.write_button)

        self.send_quick_button = _button("Envoyer", self.open_composer)
        self.bottom_bar.add_subview(self.send_quick_button)

        # Panneau de saisie placé dans la moitié haute de l'écran.
        # Il reste visible même lorsque le clavier iOS est affiché.
        self.composer_panel = ui.View()
        self.composer_panel.background_color = _color("SECONDARY_SYSTEM_BACKGROUND")
        self.composer_panel.hidden = True
        self.add_subview(self.composer_panel)

        self.composer_title = ui.Label(text="Nouveau message")
        self.composer_title.text_color = _color("LABEL")
        self.composer_panel.add_subview(self.composer_title)

        self.input = ui.TextView(text="")
        self.input.background_color = _color("TERTIARY_SYSTEM_BACKGROUND")
        self.input.text_color = _color("LABEL")
        self.composer_panel.add_subview(self.input)

        self.cancel_button = _button("Annuler", self.cancel_composer)
        self.composer_panel.add_subview(self.cancel_button)

        self.send_button = _button("Envoyer", self.send_message)
        self.composer_panel.add_subview(self.send_button)

    def layout(self) -> None:
        width = max(320, self.width)
        height = max(480, self.height)

        self.header.frame = (0, TOP_SAFE, width, HEADER_HEIGHT)
        self.title_label.frame = (16, 11, max(100, width - 220), 36)
        self.web_button.frame = (width - 178, 10, 78, 38)
        self.new_button.frame = (width - 96, 10, 86, 38)

        bottom_y = height - BOTTOM_BAR_HEIGHT
        transcript_y = TOP_SAFE + HEADER_HEIGHT
        transcript_h = max(120, bottom_y - transcript_y - STATUS_HEIGHT)

        self.transcript.frame = (10, transcript_y + 4, width - 20, transcript_h - 4)
        self.status.frame = (16, transcript_y + transcript_h, width - 32, STATUS_HEIGHT)

        self.bottom_bar.frame = (0, bottom_y, width, BOTTOM_BAR_HEIGHT)
        self.write_button.frame = (12, 10, max(140, width - 118), 50)
        self.send_quick_button.frame = (width - 96, 10, 84, 50)

        panel_w = width - 24
        panel_h = 230
        panel_y = TOP_SAFE + HEADER_HEIGHT + 18
        self.composer_panel.frame = (12, panel_y, panel_w, panel_h)
        self.composer_title.frame = (14, 10, panel_w - 28, 30)
        self.input.frame = (12, 46, panel_w - 24, 118)
        self.cancel_button.frame = (12, 174, 92, 44)
        self.send_button.frame = (panel_w - 104, 174, 92, 44)

    def open_composer(self, sender: Any) -> None:
        if self.is_sending:
            return
        self.composer_open = True
        self.composer_panel.hidden = False
        self.status.text = "Saisissez votre message"
        try:
            self.input.begin_editing()
        except Exception:
            try:
                self.input.become_first_responder()
            except Exception:
                pass

    def cancel_composer(self, sender: Any) -> None:
        self._close_composer(clear=False)
        self.status.text = "Prêt"

    def _close_composer(self, clear: bool) -> None:
        try:
            self.input.end_editing()
        except Exception:
            try:
                self.input.resign_first_responder()
            except Exception:
                pass
        if clear:
            self.input.text = ""
        self.composer_panel.hidden = True
        self.composer_open = False

    def toggle_web(self, sender: Any) -> None:
        self.web_enabled = not self.web_enabled
        self.web_button.title = "Web on" if self.web_enabled else "Web off"
        self.status.text = (
            "Recherche Web activée" if self.web_enabled else "Recherche Web désactivée"
        )

    def new_conversation(self, sender: Any) -> None:
        if self.is_sending:
            return
        self._close_composer(clear=True)
        try:
            self.app.new_conversation()
            self.status.text = "Nouvelle conversation créée"
            self.refresh_messages()
        except Exception as exc:
            self.status.text = f"Erreur nouvelle conversation : {exc}"

    def send_message(self, sender: Any) -> None:
        if self.is_sending:
            return
        text = str(self.input.text or "").strip()
        if not text:
            self.status.text = "Saisissez un message."
            return

        self._close_composer(clear=True)
        self.is_sending = True
        self.send_button.enabled = False
        self.new_button.enabled = False
        self.web_button.enabled = False
        self.write_button.enabled = False
        self.send_quick_button.enabled = False
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
            self.web_button.enabled = True
            self.write_button.enabled = True
            self.send_quick_button.enabled = True
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

    def refresh_messages(self, extra_user: str = None) -> None:
        messages = list(self.app.get_messages())
        if extra_user:
            messages.append({"role": "user", "content": extra_user})
        self.transcript.text = self._format_messages(messages)
        try:
            self.transcript.scroll_range_to_visible(
                max(0, len(self.transcript.text) - 1), 1
            )
        except Exception:
            pass

    @staticmethod
    def _format_messages(messages: List[Dict[str, Any]]) -> str:
        if not messages:
            return (
                "Bienvenue dans AssistantIA v5.\n\n"
                "Touchez « Écrire un message… » pour commencer."
            )
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
