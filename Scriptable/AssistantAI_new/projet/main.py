"""Point d'entrée AssistantAI new."""

import traceback

from ui_app import present


def main():
    try:
        present()
    except Exception:
        traceback.print_exc()
        print("Lancez diagnostic.py pour obtenir davantage d'informations.")


if __name__ == "__main__":
    main()
