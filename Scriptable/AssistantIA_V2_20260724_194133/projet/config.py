from pathlib import Path

APP_NAME = "AssistantIA V2"
APP_VERSION = "2.0.0"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
CACHE_DIR = DATA_DIR / "cache"
CONVERSATIONS_PATH = DATA_DIR / "conversations.json"
SETTINGS_PATH = DATA_DIR / "settings.json"
INDEX_DB_PATH = DATA_DIR / "rag.sqlite3"

for directory in (DATA_DIR, KNOWLEDGE_DIR, CACHE_DIR):
    directory.mkdir(parents=True, exist_ok=True)

OPENAI_API_URL = "https://api.openai.com/v1/responses"
OPENAI_EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"
OPENAI_MODEL = "gpt-4.1"
EMBEDDING_MODEL = "text-embedding-3-small"
MAX_OUTPUT_TOKENS = 1800
REQUEST_TIMEOUT_SECONDS = 120

WEB_SEARCH_DEFAULT_MODE = "auto"
VALID_WEB_MODES = {"off", "auto", "always"}

CHUNK_SIZE_CHARS = 2600
CHUNK_OVERLAP_CHARS = 320
TOP_K_CHUNKS = 8
MAX_DOCUMENT_CONTEXT_CHARS = 18000
SUPPORTED_EXTENSIONS = {
    ".txt", ".md", ".markdown", ".json", ".csv",
    ".docx", ".xlsx", ".pptx", ".pdf",
}

SYSTEM_INSTRUCTIONS = (
    "Tu es un assistant personnel fiable, précis et utile. "
    "Réponds en français sauf demande contraire. "
    "Lorsque des sources documentaires sont fournies, privilégie-les, "
    "distingue clairement les faits des inférences et cite les références [DOC n]. "
    "Lorsque la recherche Web est utilisée, appuie les affirmations récentes sur les sources disponibles."
)


def load_api_key() -> str:
    try:
        from secrets import OPENAI_API_KEY  # type: ignore
        if isinstance(OPENAI_API_KEY, str) and OPENAI_API_KEY.strip():
            return OPENAI_API_KEY.strip()
    except Exception:
        pass
    return ""
