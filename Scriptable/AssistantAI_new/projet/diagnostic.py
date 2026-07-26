"""Diagnostic non payant de compatibilité Pyto pour AssistantAI new."""

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
    print("=== AssistantAI new — Diagnostic (aucun appel OpenAI) ===")
    print("Python:", sys.version.split()[0])
    print("Plateforme:", platform.platform())
    print("Dossier:", ROOT)

    def ui_check():
        import pyto_ui as ui
        required = ("show_view", "View", "TextView", "Button", "Label")
        missing = [name for name in required if not hasattr(ui, name)]
        if missing:
            raise RuntimeError("capacités absentes: " + ", ".join(missing))
        modern_mode = bool(getattr(getattr(ui, "PresentationMode", None), "FULLSCREEN", None))
        legacy_mode = hasattr(ui, "PRESENTATION_MODE_FULLSCREEN")
        try:
            import mainthread
            mainthread_ok = hasattr(mainthread, "run_async")
        except Exception:
            mainthread_ok = False
        return "capacités présentes; mainthread={0}; fullscreen moderne={1}; legacy={2}".format(
            mainthread_ok, modern_mode, legacy_mode
        )

    check("pyto_ui", ui_check, required=False)
    for module in ("config", "storage", "conversation", "api_client", "app"):
        check("Import " + module, lambda name=module: __import__(name).__name__)
    check("Import ui_app", lambda: __import__("ui_app").__name__, required=False)

    database_dir = os.path.join(ROOT, "database")
    check("Dossier database", lambda: os.makedirs(database_dir, exist_ok=True) or database_dir)

    def sqlite_check():
        fd, path = tempfile.mkstemp(prefix="assistantai_diag_", suffix=".sqlite3", dir=database_dir)
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
    check("Réseau optionnel (DNS seulement)", lambda: socket.gethostbyname("api.openai.com"), required=False)

    required_failures = [label for label, ok, required in RESULTS if required and not ok]
    print("=== Résultat: {0} ===".format("PRÊT" if not required_failures else "À CORRIGER: " + ", ".join(required_failures)))
    return 0 if not required_failures else 1


if __name__ == "__main__":
    sys.exit(main())
