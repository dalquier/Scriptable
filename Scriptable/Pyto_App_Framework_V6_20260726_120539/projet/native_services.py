from __future__ import annotations

import urllib.parse
import webbrowser
from typing import Any


def show_alert(title: str, message: str) -> None:
    try:
        import pyto_ui as ui

        ui.alert(title, message, ["OK"])
    except Exception:
        print(f"[{title}] {message}")


def open_url(url: str) -> None:
    if not isinstance(url, str) or not url.startswith(("https://", "http://")):
        raise ValueError("URL non autorisée")
    webbrowser.open(url)


def share_text(text: str) -> None:
    try:
        import pasteboard

        pasteboard.set_string(text)
        show_alert("Texte copié", "Le résumé a été copié dans le presse-papiers.")
    except Exception:
        encoded = urllib.parse.quote(text)
        webbrowser.open(f"mailto:?body={encoded}")


def native_capabilities() -> dict[str, Any]:
    return {
        "alerts": True,
        "open_url": True,
        "share": True,
        "document_picker": False,
    }
