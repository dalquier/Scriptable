from __future__ import annotations

import sys
import traceback
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def main() -> None:
    from app import PytoAppFramework

    application = PytoAppFramework(ROOT_DIR)
    application.run()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
