from __future__ import annotations

import sys
from pathlib import Path
from time import sleep

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from ui_app import MainUI


APP = None


def main():
    global APP

    APP = MainUI()
    APP.present()

    sleep(0.25)
    native_view = getattr(APP.view, "__py_view__", None)

    try:
        while native_view is not None and bool(getattr(native_view, "isPresented", False)):
            sleep(0.20)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
