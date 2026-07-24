"""Configuration publique d'AssistantIA Studio.

Les secrets ne doivent jamais être ajoutés dans ce fichier. La clé OpenAI est
chargée depuis ``config.local.py`` lorsqu'il existe.
"""

from pathlib import Path

APP_NAME = "AssistantIA Studio"
APP_VERSION = "0.1.0"

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATA_DIR = BASE_DIR / "data"
PROMPTS_DIR = BASE_DIR / "prompts"

DATABASE_PATH = DATABASE_DIR / "assistantia.sqlite3"
SETTINGS_PATH = DATA_DIR / "settings.json"
MEMORY_PATH = DATA_DIR / "memory.json"

OPENAI_API_URL = "https://api.openai.com/v1/responses"
OPENAI_MODEL = "gpt-5-mini"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
MAX_OUTPUT_TOKENS = 1600
REQUEST_TIMEOUT_SECONDS = 90
WEB_SEARCH_MODE = "auto"

SYSTEM_PROMPT = (
    "Tu es AssistantIA Studio, un assistant fiable, clair et structuré. "
    "Distingue les faits des hypothèses et signale explicitement les limites."
)


def ensure_directories() -> None:
    """Crée les dossiers de données nécessaires au fonctionnement local."""

    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)


def load_openai_api_key() -> str:
    """Charge la clé OpenAI depuis le fichier local non versionné."""

    try:
        from config_local import OPENAI_API_KEY  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Fichier config_local.py introuvable. Créez-le dans le dossier projet "
            "avec OPENAI_API_KEY = 'sk-...'."
        ) from exc

    key = str(OPENAI_API_KEY).strip()
    if not key or key.startswith("sk-..."):
        raise RuntimeError("La clé OpenAI locale est absente ou invalide.")
    return key
