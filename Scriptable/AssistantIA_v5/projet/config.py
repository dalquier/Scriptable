"""Configuration publique AssistantIA v5."""

APP_NAME = "AssistantIA"
APP_VERSION = "5.0.0"
# Le modèle dépend des droits du compte. Modifiez cette valeur si l'API renvoie
# 403/404; l'application ne suppose pas qu'un modèle est accessible.
MODEL = "gpt-4.1-mini"
API_URL = "https://api.openai.com/v1/responses"
TIMEOUT_SECONDS = 90
MAX_OUTPUT_TOKENS = 2500
SYSTEM_INSTRUCTIONS = (
    "Tu es AssistantIA. Réponds en français, de manière claire, structurée et prudente. "
    "Pour les sujets sensibles, distingue faits, hypothèses et limites."
)

try:
    from config_local import OPENAI_API_KEY
except Exception:
    OPENAI_API_KEY = ""
