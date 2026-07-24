"""Diagnostic rapide de compatibilité Pyto pour AssistantIA v5."""

from __future__ import annotations

import os
import platform
import sys
import traceback


def check(label: str, func) -> None:
    try:
        value = func()
        print(f"[OK] {label}: {value}")
    except Exception as exc:
        print(f"[ERREUR] {label}: {exc}")
        traceback.print_exc()


def main() -> None:
    print("=== AssistantIA v5 — Diagnostic ===")
    print("Python:", sys.version)
    print("Plateforme:", platform.platform())
    print("Dossier:", os.path.dirname(os.path.abspath(__file__)))

    check("Import pyto_ui", lambda: __import__("pyto_ui"))

    def ui_capabilities():
        import pyto_ui as ui
        return {
            "show_view": hasattr(ui, "show_view"),
            "View": hasattr(ui, "View"),
            "TextView": hasattr(ui, "TextView"),
            "Button": hasattr(ui, "Button"),
            "delay": hasattr(ui, "delay"),
            "fullscreen": hasattr(ui, "PRESENTATION_MODE_FULLSCREEN"),
        }

    check("Capacités pyto_ui", ui_capabilities)
    check("Import config", lambda: __import__("config"))
    check("Import storage", lambda: __import__("storage"))
    check("Import conversation", lambda: __import__("conversation"))
    check("Import api_client", lambda: __import__("api_client"))
    check("Import app", lambda: __import__("app"))
    check("Import ui_app", lambda: __import__("ui_app"))

    def database_test():
        from storage import Storage
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "diagnostic.sqlite3")
        storage = Storage(path)
        conversation_id = storage.create_conversation("Diagnostic")
        storage.add_message(conversation_id, "user", "test")
        return storage.get_messages(conversation_id)

    check("SQLite", database_test)
    print("=== Fin du diagnostic ===")


if __name__ == "__main__":
    main()
