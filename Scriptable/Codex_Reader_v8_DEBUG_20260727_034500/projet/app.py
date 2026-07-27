# -*- coding: utf-8 -*-
"""Codex Reader v8 DEBUG pour Pyto."""

import threading
import time
import pyto_ui as ui

from debug_engine import DIAGNOSTIC_JS, parse as parse_diag
from extractor import AUTO_JS, INSTALL_MANUAL_JS, MANUAL_EXTRACT_JS, parse
from result_view import build
from storage import load_settings, save_settings, save_diagnostic

HOME_URL = "https://chatgpt.com/"
LOGIN_URL = "https://chatgpt.com/auth/login"


class App:
    def __init__(self):
        self.settings = load_settings()
        self.current_url = self.settings.get("last_url", "")

        self.root = ui.View()
        self.root.title = "Codex Reader Debug"
        self.root.background_color = ui.COLOR_SYSTEM_BACKGROUND

        self.title = ui.Label()
        self.title.text = "Codex Reader · Debug"
        self.title.frame = (18, 12, 350, 34)
        self.root.add_subview(self.title)

        self.url = ui.TextField()
        self.url.text = self.current_url
        self.url.placeholder = "https://chatgpt.com/s/..."
        self.url.frame = (14, 52, 362, 44)
        self.root.add_subview(self.url)

        self._button("Charger", (14, 104, 112, 42), self.load_link)
        self._button("Analyse auto", (134, 104, 116, 42), self.auto_extract)
        self._button("Diagnostic", (258, 104, 118, 42), self.create_diagnostic)
        self._button("Connexion", (14, 152, 110, 40), self.login)
        self._button("Mode manuel", (132, 152, 118, 40), self.manual_mode)
        self._button("Extraire", (258, 152, 118, 40), self.manual_extract)

        self.status = ui.Label()
        self.status.text = "Charge le lien, puis essaie Analyse auto."
        self.status.frame = (16, 198, 360, 56)
        self.root.add_subview(self.status)

        self.web = ui.WebView()
        self.web.frame = (0, 258, 390, 462)
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

    def set_status(self, text):
        self.status.text = text

    def login(self, sender=None):
        self.set_status("Connecte-toi dans la page affichée.")
        self.web.load_url(LOGIN_URL)

    def load_link(self, sender=None):
        url = (self.url.text or "").strip()
        if not url.startswith(("https://chatgpt.com/", "http://chatgpt.com/")):
            self.set_status("URL ChatGPT invalide.")
            return
        self.current_url = url
        self.settings["last_url"] = url
        save_settings(self.settings)
        self.set_status("Chargement en cours…")
        self.web.load_url(url)

    def auto_extract(self, sender=None):
        self.set_status("Analyse automatique…")
        def task():
            try:
                time.sleep(0.3)
                data = parse(self.web.evaluate_js(AUTO_JS))
                self.web.load_html(build(data.get("question", ""), data.get("question_html", ""), data.get("answer", ""), data.get("answer_html", ""), data.get("url", self.current_url)))
                self.set_status("Extraction automatique réussie.")
            except Exception as exc:
                self.set_status("Échec auto : " + str(exc)[:100] + ". Diagnostic ou mode manuel.")
        threading.Thread(target=task, daemon=True).start()

    def create_diagnostic(self, sender=None):
        self.set_status("Création du diagnostic DOM…")
        def task():
            try:
                data = parse_diag(self.web.evaluate_js(DIAGNOSTIC_JS))
                html_text = data.pop("html", "")
                json_path, html_path = save_diagnostic(data, html_text)
                self.set_status("Créé : " + json_path.name + " et " + html_path.name)
            except Exception as exc:
                self.set_status("Diagnostic impossible : " + str(exc)[:110])
        threading.Thread(target=task, daemon=True).start()

    def manual_mode(self, sender=None):
        try:
            self.web.evaluate_js(INSTALL_MANUAL_JS)
            self.set_status("Touchez la question grise, puis un des pouces, puis Extraire.")
        except Exception as exc:
            self.set_status("Mode manuel impossible : " + str(exc)[:105])

    def manual_extract(self, sender=None):
        self.set_status("Extraction de la sélection…")
        def task():
            try:
                data = parse(self.web.evaluate_js(MANUAL_EXTRACT_JS))
                self.web.load_html(build(data.get("question", ""), data.get("question_html", ""), data.get("answer", ""), data.get("answer_html", ""), data.get("url", self.current_url)))
                self.set_status("Extraction manuelle réussie.")
            except Exception as exc:
                self.set_status("Échec manuel : " + str(exc)[:110])
        threading.Thread(target=task, daemon=True).start()

    def present(self):
        try:
            ui.show_view(self.root, ui.PresentationMode.SHEET)
        except Exception:
            ui.show_view(self.root)


if __name__ == "__main__":
    App().present()
