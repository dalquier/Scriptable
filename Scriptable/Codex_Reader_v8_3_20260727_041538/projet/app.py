# -*- coding: utf-8 -*-
"""Codex Reader v8.3 — Pyto."""

import threading
import time

import pyto_ui as ui

from extractor import CHECK_SESSION_JS, EXTRACT_JS, parse
from result_view import build
from storage import load_settings, save_settings


HOME_URL = "https://chatgpt.com/"
LOGIN_URL = "https://chatgpt.com/auth/login"


class App:
    def __init__(self):
        self.settings = load_settings()
        self.current_url = self.settings.get("last_url", "")

        self.root = ui.View()
        self.root.title = "Codex Reader"
        self.root.background_color = ui.COLOR_SYSTEM_BACKGROUND

        self.title = ui.Label()
        self.title.text = "Codex Reader"
        self.title.frame = (18, 14, 350, 34)
        self.root.add_subview(self.title)

        self.subtitle = ui.Label()
        self.subtitle.text = "Le dernier échange, proprement formaté."
        self.subtitle.frame = (18, 48, 350, 28)
        self.root.add_subview(self.subtitle)

        self.url = ui.TextField()
        self.url.text = self.current_url
        self.url.placeholder = "https://chatgpt.com/s/..."
        self.url.frame = (14, 84, 362, 46)
        self.root.add_subview(self.url)

        self._button("Analyser", (14, 138, 362, 48), self.analyze)
        self._button("Se connecter", (14, 194, 174, 40), self.login)
        self._button("Nouvelle analyse", (196, 194, 180, 40), self.reset)

        self.status = ui.Label()
        self.status.text = "Colle un lien puis touche Analyser."
        self.status.frame = (16, 240, 360, 48)
        self.root.add_subview(self.status)

        self.web = ui.WebView()
        self.web.frame = (0, 292, 390, 428)
        try:
            self.web.flex = [
                ui.AutoResizing.FLEXIBLE_WIDTH,
                ui.AutoResizing.FLEXIBLE_HEIGHT,
            ]
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
        self.set_status("Colle un autre lien puis touche Analyser.")
        self.web.load_url(HOME_URL)

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
                time.sleep(2.8)
                state = parse(self.web.evaluate_js(CHECK_SESSION_JS))
                if not state.get("connected"):
                    self.set_status("Connexion nécessaire. Touche Se connecter.")
                    return

                self.set_status("Extraction entre la question et les pouces…")
                data = parse(self.web.evaluate_js(EXTRACT_JS))
                page = build(
                    data.get("question", ""),
                    data.get("question_html", ""),
                    data.get("answer", ""),
                    data.get("answer_html", ""),
                    data.get("url") or url,
                )
                self.web.load_html(page)
                debug = data.get("debug") or {}
                self.set_status(
                    "Terminé — question "
                    + str(debug.get("questionLength", "?"))
                    + " caractères, réponse "
                    + str(debug.get("answerLength", "?"))
                    + "."
                )
            except Exception as exc:
                self.set_status("Analyse impossible : " + str(exc)[:150])

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
    App().present()
