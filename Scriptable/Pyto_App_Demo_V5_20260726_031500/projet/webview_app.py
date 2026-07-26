from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pyto_ui as ui

from app_state import AppState
from native_services import NativeServices


class PytoAppDemo:
    """Hôte WebView et contrôleur de commandes pour la démonstration V5."""

    APP_SCHEME = "pytoapp"

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.ui_dir = root_dir / "ui"
        self.state = AppState(root_dir)
        self.webview = ui.WebView()
        self.webview.title = "Pyto App Demo"
        self.webview.delegate = self

    def run(self) -> None:
        state = self.state.register_launch()
        html = self._build_html(state)
        self.webview.load_html(html)
        ui.show_view(self.webview, ui.PRESENTATION_MODE_FULLSCREEN)

    def _build_html(self, state: dict) -> str:
        index_path = self.ui_dir / "index.html"
        css_path = self.ui_dir / "app.css"
        js_path = self.ui_dir / "app.js"

        html = index_path.read_text(encoding="utf-8")
        css = css_path.read_text(encoding="utf-8")
        js = js_path.read_text(encoding="utf-8")
        initial_state = json.dumps(state, ensure_ascii=False).replace("</", "<\\/")

        return (
            html.replace("/*__APP_CSS__*/", css)
            .replace("/*__APP_JS__*/", js)
            .replace("__INITIAL_STATE__", initial_state)
        )

    def webview_should_start_load(self, webview, url, navigation_type):
        parsed = urlparse(str(url))
        if parsed.scheme != self.APP_SCHEME:
            return True

        action = parsed.netloc or parsed.path.lstrip("/")
        query = parse_qs(parsed.query)
        self._dispatch(action, query)
        return False

    def _dispatch(self, action: str, query: dict) -> None:
        try:
            if action == "primary-action":
                state = self.state.register_action()
                NativeServices.show_alert(
                    "Action exécutée",
                    "Python a traité la commande envoyée depuis la WebView.",
                )
                self._push_state(state, "Action enregistrée")
                return

            if action == "share":
                state = self.state.add_activity("Feuille de partage ouverte", "info")
                NativeServices.share_text(NativeServices.make_share_summary(state))
                self._push_state(state, "Partage ouvert")
                return

            if action == "open-url":
                target = self._first(query, "url", "https://pyto.app")
                opened = NativeServices.open_url(target)
                state = self.state.add_activity(
                    "URL externe ouverte" if opened else "Échec ouverture URL",
                    "info" if opened else "warning",
                )
                self._push_state(state, "URL transmise à iOS")
                return

            if action == "preference":
                key = self._first(query, "key", "")
                raw_value = self._first(query, "value", "")
                value = self._decode_value(raw_value)
                state = self.state.set_preference(key, value)
                self._push_state(state, "Réglage sauvegardé")
                return

            if action == "reset":
                state = self.state.reset()
                self._push_state(state, "Données réinitialisées")
                return

            if action == "refresh":
                self._push_state(self.state.snapshot(), "Données actualisées")
                return

            raise ValueError(f"Action inconnue : {action}")
        except Exception as exc:
            try:
                self.state.add_activity(f"Erreur : {exc}", "error")
            except Exception:
                pass
            self._push_error(str(exc))

    @staticmethod
    def _first(query: dict, key: str, default: str) -> str:
        values = query.get(key)
        return str(values[0]) if values else default

    @staticmethod
    def _decode_value(value: str):
        lowered = value.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        return value

    def _evaluate(self, script: str) -> None:
        try:
            self.webview.evaluate_js(script)
        except AttributeError:
            self.webview.evaluate_javascript(script)

    def _push_state(self, state: dict, toast: str = "") -> None:
        payload = json.dumps(state, ensure_ascii=False)
        toast_payload = json.dumps(toast, ensure_ascii=False)
        self._evaluate(f"window.PytoApp.receiveState({payload}, {toast_payload});")

    def _push_error(self, message: str) -> None:
        payload = json.dumps(message, ensure_ascii=False)
        self._evaluate(f"window.PytoApp.receiveError({payload});")
