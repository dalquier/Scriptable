"""Diagnostic autonome pour vérifier l'installation Pyto."""

from __future__ import annotations

import importlib
import os
import platform
import sys
import traceback
from pathlib import Path


def check_module(name: str) -> None:
    try:
        module = importlib.import_module(name)
        origin = getattr(module, "__file__", "module intégré")
        print(f"[OK] {name} : {origin}")
    except Exception as exc:
        print(f"[ERREUR] {name} : {exc}")


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    print("=== DIAGNOSTIC ASSISTANTIA CORRIGÉ ===")
    print(f"Python : {sys.version}")
    print(f"Plateforme : {platform.platform()}")
    print(f"Dossier du projet : {base_dir}")
    print(f"Dossier courant : {Path.cwd()}")
    print(f"Écriture projet : {os.access(str(base_dir), os.W_OK)}")
    print()

    for module_name in (
        "pyto_ui",
        "sqlite3",
        "urllib.request",
        "json",
        "threading",
        "config",
        "storage",
        "conversation",
        "api_client",
        "app",
        "ui_app",
    ):
        check_module(module_name)

    print()
    try:
        import pyto_ui as ui

        print("=== PYTO_UI ===")
        for attribute in (
            "View",
            "Label",
            "Button",
            "TextView",
            "SystemColors",
            "ButtonType",
            "PresentationMode",
            "delay",
        ):
            print(f"{attribute} : {hasattr(ui, attribute)}")
    except Exception:
        traceback.print_exc()

    print()
    try:
        from config import DATABASE_PATH, ensure_directories, load_openai_api_key

        ensure_directories()
        print(f"Base SQLite : {DATABASE_PATH}")
        print(f"Dossier base accessible : {DATABASE_PATH.parent.exists()}")
        try:
            key = load_openai_api_key()
            print(f"Clé OpenAI détectée : oui ({len(key)} caractères)")
        except Exception as exc:
            print(f"Clé OpenAI détectée : non — {exc}")
    except Exception:
        traceback.print_exc()

    print("=== FIN DU DIAGNOSTIC ===")


if __name__ == "__main__":
    main()
