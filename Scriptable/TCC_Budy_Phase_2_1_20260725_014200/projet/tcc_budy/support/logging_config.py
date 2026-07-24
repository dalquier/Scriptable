import atexit
import logging
from pathlib import Path

_HANDLER = None


def configure_logging(logs_dir: Path) -> None:
    global _HANDLER
    if _HANDLER is not None:
        return
    logs_dir = Path(logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(logs_dir / "tcc_budy.log", mode="a", encoding="utf-8", delay=True)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(handler)
    _HANDLER = handler


def close_logging() -> None:
    global _HANDLER
    handler = _HANDLER
    _HANDLER = None
    if handler is None:
        return
    try:
        logging.getLogger().removeHandler(handler)
        handler.flush()
    finally:
        handler.close()


atexit.register(close_logging)
