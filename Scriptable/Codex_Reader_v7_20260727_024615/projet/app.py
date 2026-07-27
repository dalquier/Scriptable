# -*- coding: utf-8 -*-
"""Codex Reader v7 — application Pyto simplifiée."""

import threading
import time

import pyto_ui as ui

from analyzer import ANALYZE_LAST_EXCHANGE_JS, CHECK_SESSION_JS, parse_json
from browser_adapter import BrowserAdapter, JavaScriptUnavailable
from result_view import build_result_html
from storage import load_settings, save_settings

LOGIN_URL = "https://chatgpt.com/auth/login"
HOME_URL = "https://chatgpt.com/"


class CodexReaderApp:
    def __init__(self):
        self.settings = load_settings()
        self.current_url = self.settings.get("last_url") or ""
        self.connected = False
        self.result_mode = False

        self.root = ui.View()
        self.root.title = "Codex Reader"
        self.root.background_color = ui.COLOR_SYSTEM_BACKGROUND

        self.header = ui.Label()
        self.header.text = "Codex Reader"
        self.header.frame = (18, 14, 250, 34)
        self.header.flex = [ui.FLEXIBLE_WIDTH]
        self.root.add_subview(self.header)

        self.subtitle = ui.Label()
        self.subtitle.text = "Copie un lien, l’app extrait le dernier échange."
        self.subtitle.frame = (18, 46, 354, 28)
        self.subtitle.flex = [ui.FLEXIBLE_WIDTH]
        self.root.add_subview(self.subtitle)

        self.url_field = ui.TextField()
        self.url_field.text = self.current_url
        self.url_field.placeholder = "https://chatgpt.com/s/..."
        self.url_field.frame = (16, 82, 358, 46)
        self.url_field.flex = [ui.FLEXIBLE_WIDTH]
        self.root.add_subview(self.url_field)

        self.primary_button = self._button("Analyser le lien", (16, 136, 358, 48), self.analyze_link)
        self.primary_button.flex = [ui.FLEXIBLE_WIDTH]

        self.secondary_button = self._button("Se connecter", (16, 192, 174, 40), self.open_login)
        self.back_button = self._button("Nouvelle analyse", (198, 192, 176, 40), self.reset_view)
        self.back_button.flex = [ui.FLEXIBLE_LEFT_MARGIN]

        self.status = ui.Label()
        self.status.text = "Vérification de la connexion…"
        self.status.frame = (18, 238, 354, 34)
        self.status.flex = [ui.FLEXIBLE_WIDTH]
        self.root.add_subview(self.status)

        self.web = ui.WebView()
        self.web.frame = (0, 276, 390, 444)
        self.web.flex = [ui.FLEXIBLE_WIDTH, ui.FLEXIBLE_HEIGHT]
        self.root.add_subview(self.web)
        self.browser = BrowserAdapter(self.web)
        self.browser.load_url(HOME_URL)

        threading.Thread(target=self._initial_session_check, daemon=True).start()

    def _button(self, title, frame, action):
        button = ui.Button()
        button.title = title
        button.frame = frame
        button.action = action
        self.root.add_subview(button)
        return button

    def set_status(self, text):
        self.status.text = text

    def _initial_session_check(self):
        time.sleep(2.0)
        try:
            state = parse_json(self.browser.evaluate(CHECK_SESSION_JS))
            self.connected = bool(state.get("connected"))
            self.set_status("Connecté. Colle un lien puis touche Analyser." if self.connected else "Connexion nécessaire. Touche Se connecter.")
        except Exception:
            self.set_status("Colle un lien. La connexion sera vérifiée avant l’analyse.")

    def open_login(self, sender=None):
        self.result_mode = False
        self.connected = False
        self.set_status("Connecte-toi avec Continuer avec Apple, puis relance l’analyse.")
        self.browser.load_url(LOGIN_URL)

    def reset_view(self, sender=None):
        self.result_mode = False
        self.set_status("Colle un nouveau lien puis touche Analyser.")
        self.browser.load_url(HOME_URL)

    def analyze_link(self, sender=None):
        url = (self.url_field.text or "").strip()
        if not url.startswith(("https://chatgpt.com/", "http://chatgpt.com/")):
            self.set_status("Colle une URL ChatGPT ou Codex valide.")
            return

        self.current_url = url
        self.settings["last_url"] = url
        save_settings(self.settings)
        self.result_mode = False
        self.set_status("Chargement du lien…")
        self.browser.load_url(url)

        def worker():
            try:
                time.sleep(2.2)
                state = parse_json(self.browser.evaluate(CHECK_SESSION_JS))
                if not state.get("connected"):
                    self.connected = False
                    self.set_status("Tu n’es pas connecté. Touche Se connecter.")
                    return

                self.connected = True
                self.set_status("Analyse du dernier échange…")
                time.sleep(0.4)
                data = parse_json(self.browser.evaluate(ANALYZE_LAST_EXCHANGE_JS))

                html = build_result_html(
                    data.get("question", ""),
                    data.get("question_html", ""),
                    data.get("answer", ""),
                    data.get("answer_html", ""),
                    data.get("url") or url,
                )
                self.browser.load_html(html)
                self.result_mode = True
                self.set_status("Terminé. Les deux blocs sont prêts à être copiés.")
            except JavaScriptUnavailable as exc:
                self.set_status("JavaScript indisponible dans cette version de Pyto. Lance diagnostics.py.")
            except Exception as exc:
                self.set_status(f"Analyse impossible : {str(exc)[:110]}")

        threading.Thread(target=worker, daemon=True).start()

    def present(self):
        for name in ("PRESENTATION_MODE_SHEET", "PRESENTATION_MODE_PAGE_SHEET", "PRESENTATION_MODE_FORM_SHEET"):
            mode = getattr(ui, name, None)
            if mode is not None:
                ui.show_view(self.root, mode)
                return
        ui.show_view(self.root)


if __name__ == "__main__":
    CodexReaderApp().present()
