import atexit
import logging
from pathlib import Path


_LOG_HANDLER = None


def configure_logging(logs_dir: Path) -> None:
    """Configure un journal technique sans contenu conversationnel."""

    global _LOG_HANDLER

    logs_dir = Path(logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Évite d'ajouter plusieurs gestionnaires lorsque le script est relancé
    # dans la même session Pyto.
    if _LOG_HANDLER is not None:
        return

    log_path = logs_dir / "tcc_budy.log"

    handler = logging.FileHandler(
        log_path,
        mode="a",
        encoding="utf-8",
        delay=True,
    )

    handler.setLevel(logging.INFO)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
    )

    root_logger.addHandler(handler)
    _LOG_HANDLER = handler


def close_logging() -> None:
    """Ferme explicitement le fichier de journal."""

    global _LOG_HANDLER

    handler = _LOG_HANDLER
    _LOG_HANDLER = None

    if handler is None:
        return

    root_logger = logging.getLogger()

    try:
        root_logger.removeHandler(handler)
    except Exception:
        pass

    try:
        handler.flush()
    except Exception:
        pass

    try:
        handler.close()
    except Exception:
        pass


atexit.register(close_logging)
