# -*- coding: utf-8 -*-
"""Codex Reader v10 — application Pyto."""

import threading
import time

import pyto_ui as ui

from extractor import (
    AUTO_EXTRACT_JS,
    CHECK_SESSION_JS,
    MANUAL_EXTRACT_JS,
    PREPARE_JS,
    START_MANUAL_JS,
    parse,
)
from result_view import build
from storage import load_settings, save_settings

HOME_URL = "https://chatgpt.com/"
LOGIN_URL = "https://chatgpt.com/auth/login"


class CodexReaderV10:
    def __init__(self):
        self.settings = load_settings()
        self.current_url = self.settings.get("last_url", "")

        self.root = ui.View()
        self.root.title = "Codex Reader v10"
        self.root.background_color = ui.COLOR_SYSTEM_BACKGROUND

        title = ui.Label()
        title.text = "Codex Reader"
        title.frame = (18, 12, 350, 34)
        self.root.add_subview(title)

        subtitle = ui.Label()
        subtitle.text = "Dernier échange, copie intégrale."
        subtitle.frame = (18, 46, 350, 28)
        self.root.add_subview(subtitle)

        self.url = ui.TextField()
        self.url.text = self.current_url
        self.url.placeholder = "https://chatgpt.com/s/..."
        self.url.frame = (14, 82, 362, 46)
        self.root.add_subview(self.url)

        self._button("Analyser", (14, 136, 362, 46), self.analyze)
        self._button("Se connecter", (14, 190, 174, 38), self.login)
        self._button("Nouvelle analyse", (196, 190, 180, 38), self.reset)
        self._button("Choisir la question", (14, 236, 174, 38), self.start_manual)
        self._button("Extraire le choix", (196, 236, 180, 38), self.extract_manual)

        self.status = ui.Label()
        self.status.text = "Colle un lien puis touche Analyser."
        self.status.frame = (16, 280, 360, 48)
        self.root.add_subview(self.status)

        self.web = ui.WebView()
        self.web.frame = (0, 334, 390, 386)
        try:
            self.web.flex = [ui.AutoResizing.FLEXIBLE_WIDTH, ui.AutoResizing.FLEXIBLE_HEIGHT]
        except Exception:
            self.web.flex = [ui.FLEXIBLE_WIDTH, ui.FLEXIBLE_HEIGHT]
        self.root.add_subview(self.web)
        self.web.load_url(HOME_URL)

    def _button(self, title, frame, action):
        button = ui.Button()
        button.title = title
        button.frame = frame
        button.action = action
        self.root.add_subview(button)
        return button

    def set_status(self, value):
        self.status.text = value

    def login(self, sender=None):
        self.set_status("Connecte-toi avec Apple dans la page.")
        self.web.load_url(LOGIN_URL)

    def reset(self, sender=None):
        self.current_url = ""
        self.url.text = ""
        self.settings.pop("last_url", None)
        save_settings(self.settings)
        try:
            self.url.end_editing()
        except Exception:
            pass
        self.set_status("Colle un nouveau lien puis touche Analyser.")
        self.web.load_url(HOME_URL)

    def _prepare(self):
        try:
            self.web.evaluate_js(PREPARE_JS)
        except Exception:
            pass
        time.sleep(1.2)

    def _show(self, data, source):
        debug = data.get("debug") or {}
        page = build(
            data.get("question", ""),
            data.get("question_html", ""),
            data.get("answer", ""),
            data.get("answer_html", ""),
            data.get("url") or source,
            debug,
        )
        self.web.load_html(page)
        self.set_status(
            "Terminé — échange "
            + str(debug.get("exchangeIndex", "?"))
            + "/"
            + str(debug.get("exchangeCount", "?"))
            + ", "
            + str(debug.get("answerLength", "?"))
            + " caractères."
        )

    def analyze(self, sender=None):
        url = (self.url.text or "").strip()
        if not url.startswith(("https://chatgpt.com/", "http://chatgpt.com/")):
            self.set_status("URL ChatGPT invalide.")
            return

        self.current_url = url
        self.settings["last_url"] = url
        save_settings(self.settings)
        self.set_status("Chargement du lien…")
        self.web.load_url(url)

        def worker():
            try:
                time.sleep(3.0)
                state = parse(self.web.evaluate_js(CHECK_SESSION_JS))
                if not state.get("connected"):
                    self.set_status("Connexion nécessaire. Touche Se connecter.")
                    return
                self.set_status("Extraction intégrale du dernier échange…")
                self._prepare()
                data = parse(self.web.evaluate_js(AUTO_EXTRACT_JS))
                self._show(data, url)
            except Exception as exc:
                self.set_status("Échec auto : " + str(exc)[:145])

        threading.Thread(target=worker, daemon=True).start()

    def start_manual(self, sender=None):
        def worker():
            try:
                self._prepare()
                parse(self.web.evaluate_js(START_MANUAL_JS))
                self.set_status("Touche l’encadré voulu, puis Extraire le choix.")
            except Exception as exc:
                self.set_status("Mode manuel impossible : " + str(exc)[:120])

        threading.Thread(target=worker, daemon=True).start()

    def extract_manual(self, sender=None):
        def worker():
            try:
                self.set_status("Extraction intégrale de l’échange choisi…")
                data = parse(self.web.evaluate_js(MANUAL_EXTRACT_JS))
                self._show(data, self.current_url)
            except Exception as exc:
                self.set_status("Extraction manuelle impossible : " + str(exc)[:125])

        threading.Thread(target=worker, daemon=True).start()

    def present(self):
        try:
            ui.show_view(self.root, ui.PresentationMode.SHEET)
        except Exception:
            try:
                ui.show_view(self.root, ui.PRESENTATION_MODE_SHEET)
            except Exception:
                ui.show_view(self.root)


if __name__ == "__main__":
    CodexReaderV10().present()
