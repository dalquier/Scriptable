"""Point d'entrée de Dev Autopilot."""

from __future__ import annotations

import traceback
from pathlib import Path

from config import load_settings
from orchestrator import DevAutopilot


def main() -> None:
    workdir = Path(__file__).resolve().parent
    try:
        settings = load_settings()
        app = DevAutopilot(settings=settings, workdir=workdir)
        result = app.run()
        print(f"\n{result}")
    except KeyboardInterrupt:
        print("\nArrêt demandé par l'utilisateur.")
    except Exception as exc:
        print(f"\nErreur : {exc}")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
