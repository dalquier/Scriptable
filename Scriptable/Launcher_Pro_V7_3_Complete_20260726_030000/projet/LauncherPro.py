from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from core.url_scheme import item_id_from_argv, run_by_id


def main() -> None:
    item_id = item_id_from_argv()
    if item_id:
        item, result = run_by_id(item_id)
        if result.output:
            print(result.output, end="")
        if not result.success:
            raise RuntimeError(result.error or f"Échec de {item.name}")
        return

    from ui.main_view import present_launcher

    present_launcher()


if __name__ == "__main__":
    main()
