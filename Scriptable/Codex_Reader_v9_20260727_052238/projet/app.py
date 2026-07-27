# -*- coding: utf-8 -*-
"""Codex Reader v9 — application Pyto."""

import threading
import time

import pyto_ui as ui

from diagnostics import save_from_webview
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


class CodexReaderV9:
    def __init__(self):
        self.settings = load_settings()
        self.current_url = self.settings.get("last_url", "")

        self.root = ui.View()
        self.root.title = "Codex Reader v9"
        self.root.background_color = ui.COLOR_SYSTEM_BACKGROUND

        title = ui.Label()
        title.text = "Codex Reader"
        title.frame = (18, 12, 350, 34)
        self.root.add_subview(title)

        subtitle = ui.Label()
        subtitle.text = "Le dernier échange, prêt à copier."
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
        self.status.frame = (16, 280, 276, 48)
        self.root.add_subview(self.status)

        diagnostic = self._button("Diagnostic", (298, 284, 78, 38), self.diagnose)
        diagnostic.font = ui.Font.system_font_of_size(13)

        self.web = ui.WebView()
        self.web.frame = (0, 334, 390, 386)
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

    def _save_url(self, url):
        self.current_url = url
        self.settings["last_url"] = url
        save_settings(self.settings)

    def _prepare_page(self):
        try:
            self.web.evaluate_js(PREPARE_JS)
        except Exception:
            pass
        time.sleep(1.0)

    def _check_session(self):
        state = parse(self.web.evaluate_js(CHECK_SESSION_JS))
        return bool(state.get("connected"))

    def _show_result(self, data, source_url):
        page = build(
            data.get("question", ""),
            data.get("question_html", ""),
            data.get("answer", ""),
            data.get("answer_html", ""),
            data.get("url") or source_url,
        )
        self.web.load_html(page)
        debug = data.get("debug") or {}
        self.set_status(
            "Terminé — "
            + str(debug.get("selectedCount", "?"))
            + " blocs, "
            + str(debug.get("answerLength", "?"))
            + " caractères."
        )

    def analyze(self, sender=None):
        url = (self.url.text or "").strip()
        if not url.startswith(("https://chatgpt.com/", "http://chatgpt.com/")):
            self.set_status("URL ChatGPT invalide.")
            return

        self._save_url(url)
        self.set_status("Chargement du lien…")
        self.web.load_url(url)

        def worker():
            try:
                time.sleep(3.0)
                if not self._check_session():
                    self.set_status("Connexion nécessaire. Touche Se connecter.")
                    return
                self.set_status("Analyse des blocs de réponse…")
                self._prepare_page()
                data = parse(self.web.evaluate_js(AUTO_EXTRACT_JS))
                self._show_result(data, url)
            except Exception as exc:
                self.set_status("Échec auto : " + str(exc)[:115])

        threading.Thread(target=worker, daemon=True).start()

    def start_manual(self, sender=None):
        def worker():
            try:
                self._prepare_page()
                parse(self.web.evaluate_js(START_MANUAL_JS))
                self.set_status("Touche l’encadré gris, puis Extraire le choix.")
            except Exception as exc:
                self.set_status("Mode manuel impossible : " + str(exc)[:100])

        threading.Thread(target=worker, daemon=True).start()

    def extract_manual(self, sender=None):
        url = self.current_url or (self.url.text or "").strip()

        def worker():
            try:
                self.set_status("Reconstruction depuis la question choisie…")
                data = parse(self.web.evaluate_js(MANUAL_EXTRACT_JS))
                self._show_result(data, url)
            except Exception as exc:
                self.set_status("Extraction manuelle impossible : " + str(exc)[:105])

        threading.Thread(target=worker, daemon=True).start()

    def diagnose(self, sender=None):
        def worker():
            try:
                json_path, html_path = save_from_webview(self.web)
                self.set_status("Diagnostic créé : " + json_path.name)
                print("Diagnostic JSON :", json_path)
                print("Page HTML :", html_path)
            except Exception as exc:
                self.set_status("Diagnostic impossible : " + str(exc)[:105])

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
    CodexReaderV9().present()
