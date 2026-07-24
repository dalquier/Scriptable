"""Point d'entrée AssistantIA v5."""

from __future__ import annotations

import traceback

from ui_app import present


def main() -> None:
    try:
        present()
    except Exception:
        traceback.print_exc()
        print("Lancez diagnostic.py pour obtenir davantage d'informations.")


if __name__ == "__main__":
    main()
