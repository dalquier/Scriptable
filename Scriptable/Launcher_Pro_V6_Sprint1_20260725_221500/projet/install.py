from __future__ import annotations

import json

from core.paths import HISTORY_FILE, REGISTRY_FILE, SETTINGS_FILE, ensure_directories
from core.settings import DEFAULT_SETTINGS, save_settings


def initialize() -> None:
    ensure_directories()
    if not REGISTRY_FILE.exists():
        REGISTRY_FILE.write_text(json.dumps({"schema_version": 1, "scripts": []}, ensure_ascii=False, indent=2), encoding="utf-8")
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]\n", encoding="utf-8")
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
    print("Installation prête.")
    print("Exécute maintenant test_sprint1.py, puis LauncherPro.py.")


if __name__ == "__main__":
    initialize()
