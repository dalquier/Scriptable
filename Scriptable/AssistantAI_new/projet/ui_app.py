"""Interface iPhone pour AssistantAI new."""

import threading
from typing import Any, Dict, List

import pyto_ui as ui

try:
    import mainthread
except Exception:
    mainthread = None

from api_client import OpenAIClientError
from app import AssistantIAApp
from config import APP_NAME, APP_VERSION

TOP_SAFE_FALLBACK = 50
HEADER_HEIGHT = 64
TOOLBAR_HEIGHT = 58
STATUS_HEIGHT = 24
PANEL_HEIGHT = 246
MARGIN = 12


def _color(name: str, fallback: Any = None) -> Any:
    colors = getattr(ui, "SystemColors", None)
    if colors is not None and hasattr(colors, name):
        return getattr(colors, name)
    legacy = "COLOR_" + name
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


def _set_font(view: Any, size: float, bold: bool = False) -> None:
    try:
        view.font = ui.Font("HelveticaNeue-Bold" if bold else "HelveticaNeue", size)
    except Exception:
        try:
            view.font_size = size
        except Exception:
            pass


def _run_on_main(function: Any) -> None:
    """Exécute une mise à jour UI sur le thread principal de Pyto."""
    if mainthread is not None and hasattr(mainthread, "run_async"):
        mainthread.run_async(function)
        return
    # Repli pour anciennes versions : la documentation Pyto autorise la
    # modification d'une vue depuis un autre thread, mais mainthread est préféré.
    function()


class AssistantIAView(ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.title = APP_NAME
        self.background_color = _color("SYSTEM_BACKGROUND")
        self.web_enabled = False
        self.is_sending = False
        self._closed = False
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

        self.title_label = ui.Label(text=APP_NAME)
        self.title_label.text_color = _color("LABEL")
        _set_font(self.title_label, 21, True)
        self.header.add_subview(self.title_label)

        self.subtitle_label = ui.Label(text="Assistant personnel · v" + APP_VERSION)
        self.subtitle_label.text_color = _color("SECONDARY_LABEL")
        _set_font(self.subtitle_label, 12)
        self.header.add_subview(self.subtitle_label)

        self.close_button = _button("Fermer", self.close_app)
        self.header.add_subview(self.close_button)

        self.transcript_card = ui.View()
        self.transcript_card.background_color = _color("SECONDARY_SYSTEM_BACKGROUND")
        self.add_subview(self.transcript_card)

        self.transcript = ui.TextView(text="")
        self.transcript.editable = False
        self.transcript.background_color = _color("SECONDARY_SYSTEM_BACKGROUND")
        self.transcript.text_color = _color("LABEL")
        _set_font(self.transcript, 16)
        self.transcript_card.add_subview(self.transcript)

        self.status = ui.Label(text="Initialisation…")
        self.status.text_color = _color("SECONDARY_LABEL")
        _set_font(self.status, 12)
        self.add_subview(self.status)

        self.toolbar = ui.View()
        self.toolbar.background_color = _color("SECONDARY_SYSTEM_BACKGROUND")
        self.add_subview(self.toolbar)

        self.new_button = _button("Nouveau", self.new_conversation)
        self.web_button = _button("Web désactivé", self.toggle_web)
        self.write_button = _button("Écrire…", self.open_composer)
        for button in (self.new_button, self.web_button, self.write_button):
            self.toolbar.add_subview(button)

        self.composer_panel = ui.View()
        self.composer_panel.background_color = _color("SECONDARY_SYSTEM_BACKGROUND")
        self.composer_panel.hidden = True
        self.add_subview(self.composer_panel)

        self.composer_title = ui.Label(text="Nouveau message")
        self.composer_title.text_color = _color("LABEL")
        _set_font(self.composer_title, 18, True)
        self.composer_panel.add_subview(self.composer_title)

        self.composer_hint = ui.Label(text="Le champ reste visible au-dessus du clavier.")
        self.composer_hint.text_color = _color("SECONDARY_LABEL")
        _set_font(self.composer_hint, 12)
        self.composer_panel.add_subview(self.composer_hint)

        self.input = ui.TextView(text="")
        self.input.background_color = _color("TERTIARY_SYSTEM_BACKGROUND")
        self.input.text_color = _color("LABEL")
        _set_font(self.input, 16)
        self.composer_panel.add_subview(self.input)

        self.cancel_button = _button("Annuler", self.cancel_composer)
        self.send_button = _button("Envoyer", self.send_message)
        self.composer_panel.add_subview(self.cancel_button)
        self.composer_panel.add_subview(self.send_button)

    def layout(self) -> None:
        width = max(320, float(self.width or 0))
        height = max(480, float(self.height or 0))
        safe = getattr(self, "safe_area_insets", None)
        top_safe = max(TOP_SAFE_FALLBACK, float(getattr(safe, "top", 0) or 0))

        self.header.frame = (0, top_safe, width, HEADER_HEIGHT)
        self.title_label.frame = (16, 8, max(120, width - 112), 28)
        self.subtitle_label.frame = (16, 35, max(120, width - 112), 20)
        self.close_button.frame = (width - 86, 13, 74, 38)

        toolbar_y = height - TOOLBAR_HEIGHT
        status_y = toolbar_y - STATUS_HEIGHT
        content_y = top_safe + HEADER_HEIGHT + 10
        content_h = max(130, status_y - content_y - 8)
        self.transcript_card.frame = (MARGIN, content_y, width - 2 * MARGIN, content_h)
        self.transcript.frame = (10, 8, width - 2 * MARGIN - 20, content_h - 16)
        self.status.frame = (16, status_y, width - 32, STATUS_HEIGHT)

        self.toolbar.frame = (0, toolbar_y, width, TOOLBAR_HEIGHT)
        self.new_button.frame = (10, 9, 82, 40)
        self.web_button.frame = (98, 9, 118, 40)
        self.write_button.frame = (222, 9, max(88, width - 232), 40)

        panel_w = width - 2 * MARGIN
        panel_y = top_safe + HEADER_HEIGHT + 10
        self.composer_panel.frame = (MARGIN, panel_y, panel_w, PANEL_HEIGHT)
        self.composer_title.frame = (14, 10, panel_w - 28, 28)
        self.composer_hint.frame = (14, 38, panel_w - 28, 20)
        self.input.frame = (12, 64, panel_w - 24, 120)
        self.cancel_button.frame = (12, 194, 92, 40)
        self.send_button.frame = (panel_w - 104, 194, 92, 40)

    def open_composer(self, sender: Any) -> None:
        if self.is_sending:
            return
        self.composer_panel.hidden = False
        self.transcript_card.hidden = True
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
        self.transcript_card.hidden = False

    def close_app(self, sender: Any) -> None:
        self._close_composer(clear=False)
        self._closed = True
        self.app.close()
        try:
            self.close()
        except Exception as exc:
            self.status.text = "Impossible de fermer : " + str(exc)

    def toggle_web(self, sender: Any) -> None:
        self.web_enabled = not self.web_enabled
        self.web_button.title = "Web activé" if self.web_enabled else "Web désactivé"
        self.status.text = "Recherche Web activée" if self.web_enabled else "Recherche Web désactivée"

    def new_conversation(self, sender: Any) -> None:
        if self.is_sending:
            return
        self._close_composer(clear=True)
        try:
            self.app.new_conversation()
            self.status.text = "Nouvelle conversation créée"
            self.refresh_messages()
        except Exception as exc:
            self.status.text = "Erreur : " + str(exc)

    def send_message(self, sender: Any) -> None:
        if self.is_sending:
            return
        text = str(self.input.text or "").strip()
        if not text:
            self.status.text = "Saisissez un message."
            return
        self._close_composer(clear=True)
        self.is_sending = True
        self._set_buttons_enabled(False)
        self.status.text = "AssistantAI réfléchit…"
        self.refresh_messages(extra_user=text)
        threading.Thread(target=self._send_worker, args=(text,), daemon=True).start()

    def _set_buttons_enabled(self, enabled: bool) -> None:
        for button in (self.send_button, self.new_button, self.web_button, self.write_button):
            try:
                button.enabled = enabled
            except Exception:
                pass

    def _send_worker(self, text: str) -> None:
        error = None
        result = None
        try:
            result = self.app.send_message(text, enable_web_search=self.web_enabled)
        except (OpenAIClientError, RuntimeError, ValueError) as exc:
            error = str(exc)
        except Exception as exc:
            error = "Erreur inattendue : " + str(exc)

        def finish() -> None:
            if self._closed:
                return
            self.is_sending = False
            self._set_buttons_enabled(True)
            if error:
                self.status.text = error
            elif result and result.get("web_used"):
                count = len(result.get("sources", []))
                self.status.text = "Réponse avec recherche Web" + ((" · {0} source(s)".format(count)) if count else "")
            else:
                self.status.text = "Prêt"
            self.refresh_messages()

        _run_on_main(finish)

    def refresh_messages(self, extra_user: str = None) -> None:
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
            return (
                "Bienvenue dans AssistantAI new.\n\n"
                "Touchez « Écrire… » pour commencer.\n\n"
                "Activez le Web pour les informations récentes."
            )
        blocks = []  # type: List[str]
        for message in messages:
            label = "VOUS" if message.get("role") == "user" else "ASSISTANT"
            content = str(message.get("content", "")).strip()
            if content:
                blocks.append(label + "\n" + content)
        return "\n\n────────────────────\n\n".join(blocks)


def _fullscreen_mode() -> Any:
    modern = getattr(ui, "PresentationMode", None)
    if modern is not None and hasattr(modern, "FULLSCREEN"):
        return modern.FULLSCREEN
    return getattr(ui, "PRESENTATION_MODE_FULLSCREEN", "fullscreen")


def present() -> AssistantIAView:
    view = AssistantIAView()
    ui.show_view(view, _fullscreen_mode())
    return view
