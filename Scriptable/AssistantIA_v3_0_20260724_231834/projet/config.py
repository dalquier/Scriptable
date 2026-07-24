"""Configuration publique d'AssistantIA v3.0."""

from pathlib import Path

APP_NAME = "AssistantIA"
APP_VERSION = "3.0"
BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATABASE_DIR / "assistantia_v3.sqlite3"
OPENAI_API_URL = "https://api.openai.com/v1/responses"
OPENAI_MODEL = "gpt-5-mini"
MAX_OUTPUT_TOKENS = 1800
REQUEST_TIMEOUT_SECONDS = 90
SYSTEM_PROMPT = (
    "Tu es AssistantIA v3.0, un assistant fiable, clair, structuré et utile. "
    "Distingue les faits, les hypothèses et les limites."
)


def ensure_directories() -> None:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_openai_api_key() -> str:
    try:
        from config_local import OPENAI_API_KEY  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Créez projet/config_local.py à partir de config_local.example.py."
        ) from exc
    key = str(OPENAI_API_KEY).strip()
    if not key or "votre-cle" in key:
        raise RuntimeError("La clé OpenAI locale est absente ou invalide.")
    return key
