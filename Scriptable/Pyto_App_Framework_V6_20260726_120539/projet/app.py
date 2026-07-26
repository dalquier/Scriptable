from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any

import pyto_ui as ui

from native_services import native_capabilities, open_url, share_text, show_alert
from state_store import StateStore


class PytoAppFramework:
    BRIDGE_NAME = "pytoBridge"

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.ui_dir = root_dir / "ui"
        self.store = StateStore(root_dir)
        self.webview: ui.WebView | None = None
        self.root_view: ui.View | None = None

    def run(self) -> None:
        self._validate_files()
        self.store.register_launch()

        root = ui.View()
        root.title = "Pyto App Framework"
        root.background_color = ui.COLOR_SYSTEM_BACKGROUND
        root.frame = (0, 0, 390, 844)

        webview = ui.WebView()
        webview.frame = (0, 0, 390, 844)
        webview.flex = [ui.FLEXIBLE_WIDTH, ui.FLEXIBLE_HEIGHT]
        webview.did_receive_message = self._did_receive_message
        webview.register_message_handler(self.BRIDGE_NAME)

        root.add_subview(webview)
        self.root_view = root
        self.webview = webview

        webview.load_html(self._build_html())
        ui.show_view(root, ui.PRESENTATION_MODE_FULLSCREEN)

    def _validate_files(self) -> None:
        required = [
            self.ui_dir / "index.html",
            self.ui_dir / "app.css",
            self.ui_dir / "app.js",
        ]
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise FileNotFoundError("Fichiers UI manquants : " + ", ".join(missing))

    def _build_html(self) -> str:
        html = (self.ui_dir / "index.html").read_text(encoding="utf-8")
        css = (self.ui_dir / "app.css").read_text(encoding="utf-8")
        js = (self.ui_dir / "app.js").read_text(encoding="utf-8")
        initial = json.dumps(self._payload(), ensure_ascii=False).replace("</", "<\\/")
        return (
            html.replace("/*__APP_CSS__*/", css)
            .replace("/*__INITIAL_STATE__*/", initial)
            .replace("/*__APP_JS__*/", js)
        )

    def _payload(self) -> dict[str, Any]:
        return {
            "state": self.store.snapshot(),
            "capabilities": native_capabilities(),
            "version": "6.0.4",
        }

    def _did_receive_message(self, webview: ui.WebView, name: str, message: object) -> None:
        if name != self.BRIDGE_NAME:
            return

        try:
            if not isinstance(message, dict):
                raise ValueError("Message JavaScript invalide.")

            action = str(message.get("action", "")).strip()
            parameters = message.get("parameters") or {}
            if not isinstance(parameters, dict):
                raise ValueError("Paramètres JavaScript invalides.")

            self._handle_action(action, parameters)
        except Exception as exc:
            traceback.print_exc()
            show_alert("Erreur", str(exc))
            self._send_event("appError", {"message": str(exc)})

    def _handle_action(self, action: str, parameters: dict[str, Any]) -> None:
        if action == "ready":
            self._send_state()
            return

        if action == "close":
            self._close_application()
            return

        if action == "primary-action":
            self.store.add_activity("Action principale exécutée")
            show_alert("Action réussie", "La commande Python a été exécutée.")
        elif action == "share":
            state = self.store.snapshot()
            share_text(
                f"Pyto App Framework V6 — {state['action_count']} actions, "
                f"{state['launch_count']} ouvertures."
            )
            self.store.add_activity("Résumé partagé")
        elif action == "open-pyto":
            open_url("https://pyto.app")
            self.store.add_activity("Site Pyto ouvert")
        elif action == "set-preference":
            key = self._required(parameters, "key")
            value = self._required(parameters, "value")
            self.store.update_preference(key, value)
        elif action == "reset":
            self.store.reset()
        else:
            raise ValueError(f"Action inconnue : {action}")

        self._send_state()

    def _close_application(self) -> None:
        root = self.root_view
        if root is None:
            return

        # Détache d'abord le pont pour empêcher un nouveau callback pendant
        # la fermeture, puis ferme exactement la vue présentée par show_view().
        self.webview = None
        self.root_view = None
        root.close()

    @staticmethod
    def _required(parameters: dict[str, Any], key: str) -> str:
        value = parameters.get(key)
        if value is None or str(value).strip() == "":
            raise ValueError(f"Paramètre manquant : {key}")
        return str(value)

    def _send_state(self) -> None:
        self._send_event("stateChanged", self._payload())

    def _send_event(self, name: str, detail: dict[str, Any]) -> None:
        if self.webview is None:
            return

        event_name = json.dumps(name, ensure_ascii=False)
        payload = json.dumps(detail, ensure_ascii=False).replace("</", "<\\/")
        script = (
            "window.dispatchEvent(new CustomEvent(" + event_name + ","
            "{detail:" + payload + "}));"
        )
        self.webview.evaluate_js(script)
