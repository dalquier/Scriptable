from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
DATABASE_PATH = DATA_DIR / "assistantia.db"
CACHE_DIR = DATA_DIR / "cache"
ATTACHMENTS_DIR = DATA_DIR / "attachments"
EXPORTS_DIR = DATA_DIR / "exports"
LOGS_DIR = DATA_DIR / "logs"
TEMP_DIR = DATA_DIR / "temp"
THUMBNAILS_DIR = DATA_DIR / "thumbnails"


def ensure_storage():
    """Crée l'arborescence de stockage locale de l'application."""
    for path in (
        DATA_DIR,
        CACHE_DIR,
        ATTACHMENTS_DIR,
        EXPORTS_DIR,
        LOGS_DIR,
        TEMP_DIR,
        THUMBNAILS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


__all__ = [
    "APP_DIR",
    "DATA_DIR",
    "DATABASE_PATH",
    "CACHE_DIR",
    "ATTACHMENTS_DIR",
    "EXPORTS_DIR",
    "LOGS_DIR",
    "TEMP_DIR",
    "THUMBNAILS_DIR",
    "ensure_storage",
]
