from __future__ import annotations

import json

from core.paths import HISTORY_FILE, REGISTRY_FILE, SETTINGS_FILE, ensure_directories
from core.settings import DEFAULTS


def main() -> None:
    ensure_directories()
    if not REGISTRY_FILE.exists():
        REGISTRY_FILE.write_text(json.dumps({"schema_version": 2, "items": []}, ensure_ascii=False, indent=2), encoding="utf-8")
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")
    if not SETTINGS_FILE.exists():
        SETTINGS_FILE.write_text(json.dumps(DEFAULTS, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Launcher Pro V7 est prêt.")
    print("Lance maintenant LauncherPro.py")


if __name__ == "__main__":
    main()
