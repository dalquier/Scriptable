from __future__ import annotations

import json
import traceback
import urllib.parse
from pathlib import Path
from typing import Any

import pyto_ui as ui

from native_services import native_capabilities, open_url, share_text, show_alert
from state_store import StateStore


class PytoAppFramework:
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

        webview = ui.WebView()
        webview.flex = [ui.FLEXIBLE_WIDTH, ui.FLEXIBLE_HEIGHT]
        webview.frame = root.bounds
        webview.delegate = self

        root.add_subview(webview)
        self.root_view = root
        self.webview = webview

        html = self._build_html()
        webview.load_html(html)
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
            "version": "6.0.0",
        }

    def web_view_should_start_load(self, webview: ui.WebView, url: str, navigation_type: int) -> bool:
        if not url.startswith("pytoapp://"):
            return True
        try:
            self._handle_url(url)
        except Exception as exc:
            traceback.print_exc()
            show_alert("Erreur", str(exc))
            self._send_event("appError", {"message": str(exc)})
        return False

    def _handle_url(self, url: str) -> None:
        parsed = urllib.parse.urlparse(url)
        action = parsed.netloc or parsed.path.lstrip("/")
        query = urllib.parse.parse_qs(parsed.query)

        if action == "ready":
            self._send_state()
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
            key = self._first(query, "key")
            value = self._first(query, "value")
            self.store.update_preference(key, value)
        elif action == "reset":
            self.store.reset()
        else:
            raise ValueError(f"Action inconnue : {action}")

        self._send_state()

    @staticmethod
    def _first(query: dict[str, list[str]], key: str) -> str:
        values = query.get(key)
        if not values:
            raise ValueError(f"Paramètre manquant : {key}")
        return values[0]

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
        self.webview.evaluate_javascript(script)
