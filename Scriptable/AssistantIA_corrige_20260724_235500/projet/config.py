"""Configuration publique d'AssistantIA corrigé."""

from pathlib import Path

APP_NAME = "AssistantIA"
APP_VERSION = "3.1.0"

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATABASE_DIR / "assistantia.sqlite3"

OPENAI_API_URL = "https://api.openai.com/v1/responses"
OPENAI_MODEL = "gpt-5-mini"
MAX_OUTPUT_TOKENS = 1800
REQUEST_TIMEOUT_SECONDS = 90
WEB_SEARCH_TOOL_TYPE = "web_search_preview"

SYSTEM_PROMPT = (
    "Tu es AssistantIA, un assistant fiable, clair et structuré. "
    "Distingue les faits des hypothèses et indique explicitement tes limites."
)


def ensure_directories() -> None:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_openai_api_key() -> str:
    """Charge la clé depuis config_local.py, jamais depuis GitHub."""

    try:
        from config_local import OPENAI_API_KEY  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Fichier config_local.py introuvable. Copiez config_local.example.py "
            "en config_local.py puis renseignez votre clé OpenAI."
        ) from exc

    key = str(OPENAI_API_KEY).strip()
    if not key or key in {"sk-", "sk-proj-", "VOTRE_CLE_OPENAI_ICI"}:
        raise RuntimeError("La clé OpenAI locale est absente ou invalide.")
    if not key.startswith("sk-"):
        raise RuntimeError("La clé OpenAI doit commencer par 'sk-'.")
    return key
