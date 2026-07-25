from __future__ import annotations

import tempfile
from pathlib import Path

from core.backup import create_registry_backup
from core.history import load_history
from core.importer import import_script
from core.logger import read_log
from core.paths import ensure_directories
from core.registry import Registry
from core.runner import run_script


def main() -> None:
    print("=== TEST LAUNCHER PRO V6 — SPRINT 1 ===")
    ensure_directories()
    registry = Registry.load()

    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "demo_launcher_pro.py"
        source.write_text("print('Bonjour depuis le script de test')\n", encoding="utf-8")
        entry = import_script(source, name="Script de démonstration", category="Tests", registry=registry)
        print("Import : OK", entry.id)

        result = run_script(entry)
        registry.save()
        assert result.success, result.error
        assert "Bonjour" in result.output
        print("Exécution : OK")
        print("Durée :", result.duration)

        history = load_history()
        assert any(item.get("script_id") == entry.id for item in history)
        print("Historique : OK")

        backup = create_registry_backup()
        assert backup is not None and backup.exists()
        print("Sauvegarde : OK", backup.name)

        registry.remove(entry.id)
        print("Nettoyage du script de test : OK")

    assert "Exécution Script de démonstration" in read_log()
    print("Journal : OK")
    print("=== SPRINT 1 VALIDÉ ===")


if __name__ == "__main__":
    main()
