APP_NAME = "AssistantIA"
APP_VERSION = "6.0.0"
MODEL = "gpt-5.6"
API_URL = "https://api.openai.com/v1/responses"
TIMEOUT_SECONDS = 120
MAX_OUTPUT_TOKENS = 3000
SYSTEM_INSTRUCTIONS = "Réponds en français de manière claire, structurée et prudente."

try:
    from config_local import OPENAI_API_KEY
except Exception:
    OPENAI_API_KEY = ""
