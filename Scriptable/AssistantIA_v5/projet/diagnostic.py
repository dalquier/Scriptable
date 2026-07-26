"""Diagnostic non payant de compatibilité Pyto pour AssistantIA v5."""

from __future__ import annotations

import os
import platform
import socket
import sqlite3
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS = []


def check(label, function, required=True):
    try:
        detail = function()
        RESULTS.append((label, True, required))
        print("[OK] {0}: {1}".format(label, detail))
    except Exception as exc:
        RESULTS.append((label, False, required))
        print("[{0}] {1}: {2}".format("ERREUR" if required else "INFO", label, exc))


def main():
    print("=== AssistantIA v5 — Diagnostic (aucun appel OpenAI) ===")
    print("Python:", sys.version.split()[0])
    print("Plateforme:", platform.platform())
    print("Dossier:", ROOT)

    def ui_check():
        import pyto_ui as ui
        required = ("show_view", "View", "TextView", "Button", "Label")
        missing = [name for name in required if not hasattr(ui, name)]
        if missing:
            raise RuntimeError("capacités absentes: " + ", ".join(missing))
        return "capacités principales présentes; delay={0}, fullscreen={1}".format(
            hasattr(ui, "delay"), hasattr(ui, "PRESENTATION_MODE_FULLSCREEN"))

    check("pyto_ui", ui_check, required=False)
    for module in ("config", "storage", "conversation", "api_client", "app"):
        check("Import " + module, lambda name=module: __import__(name).__name__)
    # ui_app est attendu uniquement dans Pyto.
    check("Import ui_app", lambda: __import__("ui_app").__name__, required=False)

    database_dir = os.path.join(ROOT, "database")
    check("Dossier database", lambda: os.makedirs(database_dir, exist_ok=True) or database_dir)

    def sqlite_check():
        fd, path = tempfile.mkstemp(prefix="assistantia_diag_", suffix=".sqlite3", dir=database_dir)
        os.close(fd)
        try:
            connection = sqlite3.connect(path)
            with connection:
                connection.execute("CREATE TABLE test(value TEXT)")
                connection.execute("INSERT INTO test VALUES (?)", ("ok",))
                value = connection.execute("SELECT value FROM test").fetchone()[0]
            connection.close()
            return "écriture/lecture=" + value
        finally:
            if os.path.exists(path):
                os.remove(path)

    check("SQLite temporaire", sqlite_check)

    def private_config_check():
        path = os.path.join(ROOT, "config_local.py")
        if not os.path.isfile(path):
            raise RuntimeError("absent (copiez config_local.example.py)")
        from config import OPENAI_API_KEY
        if not OPENAI_API_KEY.strip():
            raise RuntimeError("clé vide")
        return "clé présente; format plausible={0}; valeur non affichée".format(OPENAI_API_KEY.startswith("sk-"))

    check("Configuration privée", private_config_check, required=False)

    def model_check():
        from config import API_URL, MODEL
        if not MODEL.strip() or not API_URL.startswith("https://api.openai.com/v1/responses"):
            raise RuntimeError("modèle ou endpoint invalide")
        return "modèle configuré: " + MODEL + " (accès à confirmer par le compte)"

    check("Configuration Responses", model_check)

    def network_check():
        # Résolution DNS uniquement: pas de requête HTTP et donc aucun coût.
        return socket.gethostbyname("api.openai.com")

    check("Réseau optionnel (DNS seulement)", network_check, required=False)
    required_failures = [label for label, ok, required in RESULTS if required and not ok]
    print("=== Résultat: {0} ===".format("PRÊT" if not required_failures else "À CORRIGER: " + ", ".join(required_failures)))
    return 0 if not required_failures else 1


if __name__ == "__main__":
    sys.exit(main())
