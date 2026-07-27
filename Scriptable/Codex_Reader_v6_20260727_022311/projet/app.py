# -*- coding: utf-8 -*-
"""Codex Reader v6 — application Pyto."""

import threading
import time

import pyto_ui as ui

from browser_adapter import BrowserAdapter, JavaScriptUnavailable
from renderer import build_result_html
from selector import INSTALL_SELECTOR_JS, EXTRACT_SELECTED_JS, parse_payload
from storage import add_history, export_pair, load_settings, save_settings

LOGIN_URL = "https://chatgpt.com/auth/login"
DEFAULT_URL = "https://chatgpt.com/"


class CodexReaderApp:
    def __init__(self):
        self.settings = load_settings()
        self.current_url = self.settings.get("last_url") or DEFAULT_URL
        self.result_mode = False
        self.question = ""
        self.answer = ""

        self.root = ui.View()
        self.root.title = "Codex Reader v6"
        self.root.background_color = ui.COLOR_SYSTEM_BACKGROUND

        self.url_field = ui.TextField()
        self.url_field.text = self.current_url
        self.url_field.placeholder = "https://chatgpt.com/s/..."
        self.url_field.frame = (12, 12, 250, 44)
        self.url_field.flex = [ui.FLEXIBLE_WIDTH]
        self.root.add_subview(self.url_field)

        self.open_button = self._button("Ouvrir", (270, 12, 108, 44), self.open_url)
        self.open_button.flex = [ui.FLEXIBLE_LEFT_MARGIN]

        self.login_button = self._button("Connexion", (12, 64, 98, 40), self.open_login)
        self.select_button = self._button("Sélectionner", (116, 64, 106, 40), self.start_selection)
        self.show_button = self._button("Afficher", (228, 64, 82, 40), self.extract_selected)
        self.back_button = self._button("Retour", (316, 64, 62, 40), self.return_to_page)
        self.back_button.flex = [ui.FLEXIBLE_LEFT_MARGIN]

        self.export_button = self._button("Exporter les fichiers", (12, 110, 180, 38), self.export_current)

        self.status = ui.Label()
        self.status.text = "Connexion → Ouvrir → Sélectionner → toucher la question → Afficher"
        self.status.frame = (12, 151, 366, 38)
        self.status.flex = [ui.FLEXIBLE_WIDTH]
        self.root.add_subview(self.status)

        self.web = ui.WebView()
        self.web.frame = (0, 192, 390, 528)
        self.web.flex = [ui.FLEXIBLE_WIDTH, ui.FLEXIBLE_HEIGHT]
        self.root.add_subview(self.web)
        self.browser = BrowserAdapter(self.web)

        # La même WebView est conservée pendant toute l’exécution. Pyto utilise
        # normalement son stockage web persistant entre les lancements.
        if self.settings.get("auto_open_last") and self.current_url != DEFAULT_URL:
            self.browser.load_url(self.current_url)
        else:
            self.browser.load_url(LOGIN_URL)

    def _button(self, title, frame, action):
        button = ui.Button()
        button.title = title
        button.frame = frame
        button.action = action
        self.root.add_subview(button)
        return button

    def set_status(self, text):
        self.status.text = text

    def open_login(self, sender=None):
        self.result_mode = False
        self.set_status("Connexion ChatGPT : utilise Continuer avec Apple.")
        self.browser.load_url(LOGIN_URL)

    def open_url(self, sender=None):
        url = (self.url_field.text or "").strip()
        if not url.startswith(("https://chatgpt.com/", "http://chatgpt.com/")):
            self.set_status("Entre une URL chatgpt.com valide.")
            return
        self.current_url = url
        self.settings["last_url"] = url
        save_settings(self.settings)
        self.result_mode = False
        self.set_status("Ouverture du lien…")
        self.browser.load_url(url)

    def start_selection(self, sender=None):
        if self.result_mode:
            self.set_status("Appuie d’abord sur Retour.")
            return

        def worker():
            try:
                self.browser.evaluate(INSTALL_SELECTOR_JS)
                self.set_status("Touchez maintenant l’encadré gris de la question voulue.")
            except JavaScriptUnavailable as exc:
                self.set_status("JavaScript indisponible. Lance diagnostics.py. " + str(exc)[:80])
            except Exception as exc:
                self.set_status(f"Erreur sélection : {type(exc).__name__} — {str(exc)[:90]}")

        threading.Thread(target=worker, daemon=True).start()

    def extract_selected(self, sender=None):
        if self.result_mode:
            self.set_status("Le résultat est déjà affiché.")
            return
        self.set_status("Lecture de la question et de la réponse…")

        def worker():
            try:
                time.sleep(0.15)
                data = parse_payload(self.browser.evaluate(EXTRACT_SELECTED_JS))
                self.question = data.get("question", "")
                self.answer = data.get("answer", "")
                self.current_url = data.get("url") or self.current_url
                add_history(self.current_url, data.get("title", ""))
                html = build_result_html(
                    self.question,
                    data.get("question_html", ""),
                    self.answer,
                    data.get("answer_html", ""),
                    self.current_url,
                )
                self.result_mode = True
                self.browser.load_html(html)
                self.set_status("Extraction terminée. Utilise les boutons Copier sous les cartes.")
            except JavaScriptUnavailable as exc:
                self.set_status("JavaScript indisponible. Lance diagnostics.py. " + str(exc)[:80])
            except Exception as exc:
                self.set_status(f"Extraction impossible : {str(exc)[:110]}")

        threading.Thread(target=worker, daemon=True).start()

    def return_to_page(self, sender=None):
        self.result_mode = False
        self.set_status("Retour à la page. Tu peux sélectionner une autre question.")
        self.browser.load_url(self.current_url)

    def export_current(self, sender=None):
        if not self.question and not self.answer:
            self.set_status("Aucun résultat à exporter.")
            return
        try:
            md, txt = export_pair(self.question, self.answer, self.current_url)
            self.set_status(f"Fichiers créés : {md.name} et {txt.name}")
        except Exception as exc:
            self.set_status(f"Erreur d’export : {exc}")

    def present(self):
        for name in ("PRESENTATION_MODE_SHEET", "PRESENTATION_MODE_PAGE_SHEET", "PRESENTATION_MODE_FORM_SHEET"):
            mode = getattr(ui, name, None)
            if mode is not None:
                ui.show_view(self.root, mode)
                return
        ui.show_view(self.root)


if __name__ == "__main__":
    CodexReaderApp().present()
