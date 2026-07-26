# -*- coding: utf-8 -*-
"""Codex Reader v5 — point d'entrée Pyto."""

import threading
import time

import pyto_ui as ui

from browser_adapter import BrowserAdapter, JavaScriptUnavailable
from extractor import EXTRACTION_JS, parse_result
from renderer import build_result_html
from storage import (
    add_history,
    export_markdown,
    export_text,
    load_settings,
    save_settings,
)

LOGIN_URL = "https://chatgpt.com/auth/login"
DEFAULT_URL = "https://chatgpt.com/s/cd_6a668b4cabfc81919f41445045d7c6c0"


class CodexReaderApp:
    def __init__(self):
        self.settings = load_settings()
        self.current_url = self.settings.get("last_url") or DEFAULT_URL
        self.question = ""
        self.answer = ""
        self.result_mode = False

        self.root = ui.View()
        self.root.title = "Codex Reader v5"
        self.root.background_color = ui.COLOR_SYSTEM_BACKGROUND

        self.url_field = ui.TextField()
        self.url_field.text = self.current_url
        self.url_field.placeholder = "https://chatgpt.com/s/..."
        self.url_field.frame = (10, 10, 260, 42)
        self.url_field.flex = [ui.FLEXIBLE_WIDTH]
        self.root.add_subview(self.url_field)

        self.open_button = self._button("Ouvrir", (278, 10, 102, 42), self.open_url)
        self.open_button.flex = [ui.FLEXIBLE_LEFT_MARGIN]

        self.login_button = self._button("Connexion", (10, 59, 102, 40), self.open_login)
        self.extract_button = self._button("Extraire", (118, 59, 92, 40), self.extract_page)
        self.page_button = self._button("Retour", (216, 59, 74, 40), self.return_to_page)
        self.export_button = self._button("Exporter", (296, 59, 84, 40), self.export_current)
        self.export_button.flex = [ui.FLEXIBLE_LEFT_MARGIN]

        self.status = ui.Label()
        self.status.text = "Connexion → Ouvrir → Extraire"
        self.status.frame = (12, 102, 366, 30)
        self.status.flex = [ui.FLEXIBLE_WIDTH]
        self.root.add_subview(self.status)

        self.web = ui.WebView()
        self.web.frame = (0, 134, 390, 586)
        self.web.flex = [ui.FLEXIBLE_WIDTH, ui.FLEXIBLE_HEIGHT]
        self.root.add_subview(self.web)
        self.browser = BrowserAdapter(self.web)
        self.browser.load_url(LOGIN_URL)

    def _button(self, title, frame, action):
        button = ui.Button()
        button.title = title
        button.frame = frame
        button.action = action
        self.root.add_subview(button)
        return button

    def set_status(self, value):
        self.status.text = value

    def open_login(self, sender=None):
        self.result_mode = False
        self.set_status("Connecte-toi avec Apple dans la page.")
        self.browser.load_url(LOGIN_URL)

    def open_url(self, sender=None):
        url = (self.url_field.text or "").strip()
        if not url.startswith(("https://chatgpt.com/", "http://chatgpt.com/")):
            self.set_status("URL ChatGPT invalide.")
            return
        self.current_url = url
        self.settings["last_url"] = url
        save_settings(self.settings)
        self.result_mode = False
        self.set_status("Ouverture du lien…")
        self.browser.load_url(url)

    def return_to_page(self, sender=None):
        self.result_mode = False
        self.set_status("Retour à la page Codex.")
        self.browser.load_url(self.current_url)

    def extract_page(self, sender=None):
        if self.result_mode:
            self.set_status("Appuie sur Retour avant une nouvelle extraction.")
            return
        self.set_status("Extraction en cours…")

        def worker():
            try:
                time.sleep(0.2)
                raw = self.browser.evaluate(EXTRACTION_JS)
                data = parse_result(raw)
                self.question = data["question"] or "Question non détectée automatiquement."
                self.answer = data["answer"] or "Réponse non détectée automatiquement."
                self.current_url = data["url"] or self.current_url
                if not data["question"] and not data["answer"]:
                    self.set_status("Aucun message détecté. Fais défiler la page puis réessaie.")
                    return
                add_history(self.current_url, data["title"])
                self.result_mode = True
                self.browser.load_html(build_result_html(self.question, self.answer, self.current_url))
                self.set_status(
                    f"Extraction terminée : {data['user_count']} question(s), "
                    f"{data['assistant_count']} réponse(s)."
                )
            except JavaScriptUnavailable as exc:
                self.set_status("JavaScript indisponible : lance diagnostics.py. " + str(exc)[:90])
            except Exception as exc:
                self.set_status(f"Erreur : {type(exc).__name__} — {str(exc)[:110]}")

        threading.Thread(target=worker, daemon=True).start()

    def export_current(self, sender=None):
        if not self.question and not self.answer:
            self.set_status("Rien à exporter : effectue d’abord une extraction.")
            return
        try:
            md_path = export_markdown(self.question, self.answer, self.current_url)
            txt_path = export_text(self.question, self.answer, self.current_url)
            self.set_status(f"Exports créés : {md_path.name} et {txt_path.name}")
        except Exception as exc:
            self.set_status(f"Erreur export : {exc}")

    def present(self):
        for name in (
            "PRESENTATION_MODE_SHEET",
            "PRESENTATION_MODE_PAGE_SHEET",
            "PRESENTATION_MODE_FORM_SHEET",
        ):
            mode = getattr(ui, name, None)
            if mode is not None:
                ui.show_view(self.root, mode)
                return
        ui.show_view(self.root)


if __name__ == "__main__":
    CodexReaderApp().present()
