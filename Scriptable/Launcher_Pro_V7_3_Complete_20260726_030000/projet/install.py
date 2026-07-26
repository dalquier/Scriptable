from __future__ import annotations

import json

from core.paths import HISTORY_FILE, REGISTRY_FILE, SETTINGS_FILE, ensure_directories
from core.settings import DEFAULT_SETTINGS


def main() -> None:
    ensure_directories()
    if not REGISTRY_FILE.exists():
        REGISTRY_FILE.write_text(json.dumps({"version": 1, "items": []}, ensure_ascii=False, indent=2), encoding="utf-8")
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")
    if not SETTINGS_FILE.exists():
        SETTINGS_FILE.write_text(json.dumps(DEFAULT_SETTINGS, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Installation prête. Lance maintenant LauncherPro.py")


if __name__ == "__main__":
    main()
