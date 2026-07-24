"""Point d'entrée principal d'AssistantIA v3.0 dans Pyto."""

from __future__ import annotations

import traceback

from ui_app import present


def main() -> int:
    try:
        present()
        return 0
    except RuntimeError as exc:
        print(f"Configuration incomplète : {exc}")
        return 2
    except Exception as exc:
        print(f"Échec du démarrage : {exc}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    main()
