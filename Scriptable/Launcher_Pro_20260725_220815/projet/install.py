from __future__ import annotations

import compileall
import os
import sys

from launcher_storage import DATA_DIR, REGISTRY_PATH, SCRIPTS_DIR, ensure_layout


def main() -> None:
    base = os.path.dirname(os.path.abspath(__file__))
    ensure_layout()
    ok = compileall.compile_dir(base, quiet=1, force=True)
    print("=== Launcher Pro V5 ===")
    print(f"Python : {sys.version.split()[0]}")
    print(f"Projet : {base}")
    print(f"Données : {DATA_DIR}")
    print(f"Scripts : {SCRIPTS_DIR}")
    print(f"Registre : {REGISTRY_PATH}")
    if not ok:
        raise RuntimeError("Au moins un fichier Python ne compile pas.")
    print("Installation prête. Lance maintenant LauncherPro.py")


if __name__ == "__main__":
    main()
