# -*- coding: utf-8 -*-
"""Codex Reader v8.1 — application Pyto."""

import threading
import time

import pyto_ui as ui

from extractor import (
    CHECK_SESSION_JS,
    EXTRACT_LAST_EXCHANGE_JS,
    PREPARE_LAST_EXCHANGE_JS,
    parse_json,
)
from result_view import build_result_html
from storage import load_settings, save_settings

HOME_URL = "https://chatgpt.com/"
LOGIN_URL = "https://chatgpt.com/auth/login"


class CodexReaderApp:
    def __init__(self):
        self.settings = load_settings()
        self.current_url = self.settings.get("last_url", "")
        self.result_mode = False

        self.root = ui.View()
        self.root.title = "Codex Reader"
        self.root.background_color = ui.COLOR_SYSTEM_BACKGROUND

        self.title = ui.Label()
        self.title.text = "Codex Reader"
        self.title.frame = (18, 12, 350, 34)
        self.title.flex = [ui.FLEXIBLE_WIDTH]
        self.root.add_subview(self.title)

        self.subtitle = ui.Label()
        self.subtitle.text = "Le dernier échange, prêt à copier."
        self.subtitle.frame = (18, 46, 350, 28)
        self.subtitle.flex = [ui.FLEXIBLE_WIDTH]
        self.root.add_subview(self.subtitle)

        self.url_field = ui.TextField()
        self.url_field.text = self.current_url
        self.url_field.placeholder = "Colle le lien Codex"
        self.url_field.frame = (16, 82, 358, 48)
        self.url_field.flex = [ui.FLEXIBLE_WIDTH]
        self.root.add_subview(self.url_field)

        self.analyze_button = self._button("Analyser", (16, 138, 358, 48), self.analyze)
        self.analyze_button.flex = [ui.FLEXIBLE_WIDTH]

        self.login_button = self._button("Se connecter avec Apple", (16, 194, 220, 40), self.open_login)
        self.new_button = self._button("Nouvelle analyse", (244, 194, 130, 40), self.reset)
        self.new_button.flex = [ui.FLEXIBLE_LEFT_MARGIN]

        self.status = ui.Label()
        self.status.text = "Vérification de la connexion…"
        self.status.frame = (18, 240, 354, 34)
        self.status.flex = [ui.FLEXIBLE_WIDTH]
        self.root.add_subview(self.status)

        self.web = ui.WebView()
        self.web.frame = (0, 278, 390, 442)
        self.web.flex = [ui.FLEXIBLE_WIDTH, ui.FLEXIBLE_HEIGHT]
        self.root.add_subview(self.web)
        self.web.load_url(HOME_URL)

        threading.Thread(target=self._check_session_after_start, daemon=True).start()

    def _button(self, title, frame, action):
        button = ui.Button()
        button.title = title
        button.frame = frame
        button.action = action
        self.root.add_subview(button)
        return button

    def set_status(self, text):
        self.status.text = text

    def evaluate(self, script):
        return self.web.evaluate_js(script)

    def _check_session_after_start(self):
        time.sleep(2.0)
        try:
            state = parse_json(self.evaluate(CHECK_SESSION_JS))
            if state.get("connected"):
                self.set_status("Connecté. Colle un lien puis touche Analyser.")
            else:
                self.set_status("Connexion nécessaire. Touche Se connecter avec Apple.")
        except Exception:
            self.set_status("Colle un lien. La connexion sera vérifiée pendant l’analyse.")

    def open_login(self, sender=None):
        self.result_mode = False
        self.set_status("Connecte-toi avec Apple dans la page ci-dessous.")
        self.web.load_url(LOGIN_URL)

    def reset(self, sender=None):
        self.result_mode = False
        self.set_status("Colle un nouveau lien puis touche Analyser.")
        self.web.load_url(HOME_URL)

    def analyze(self, sender=None):
        url = (self.url_field.text or "").strip()
        if not url.startswith(("https://chatgpt.com/", "http://chatgpt.com/")):
            self.set_status("Colle une URL chatgpt.com valide.")
            return

        self.current_url = url
        self.settings["last_url"] = url
        save_settings(self.settings)
        self.result_mode = False
        self.set_status("Chargement du lien…")
        self.web.load_url(url)

        def worker():
            try:
                time.sleep(2.6)
                state = parse_json(self.evaluate(CHECK_SESSION_JS))
                if not state.get("connected"):
                    self.set_status("Tu n’es pas connecté. Touche Se connecter avec Apple.")
                    return

                self.set_status("Repérage de la question et des pouces…")
                parse_json(self.evaluate(PREPARE_LAST_EXCHANGE_JS))

                # Laisse le temps au clic sur l'encadré de révéler le texte complet.
                time.sleep(0.8)
                self.set_status("Extraction de la réponse complète…")
                data = parse_json(self.evaluate(EXTRACT_LAST_EXCHANGE_JS))

                result = build_result_html(
                    data.get("question", ""),
                    data.get("question_html", ""),
                    data.get("answer", ""),
                    data.get("answer_html", ""),
                    data.get("url") or url,
                )
                self.web.load_html(result)
                self.result_mode = True
                self.set_status("Terminé. Utilise les boutons Copier sous les deux blocs.")
            except Exception as exc:
                self.set_status(f"Analyse impossible : {type(exc).__name__} — {str(exc)[:100]}")

        threading.Thread(target=worker, daemon=True).start()

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
