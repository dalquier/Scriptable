"""Public AI interface shared by App-perso projects."""

from .config import AIConfigurationError, AISettings, load_ai_settings
from .gateway import AIGateway, AIRequest, AIResult, ModelRouter, SourceConnector, TaskProfile

__all__ = [
    "AIGateway",
    "AIConfigurationError",
    "AIRequest",
    "AIResult",
    "AISettings",
    "ModelRouter",
    "SourceConnector",
    "TaskProfile",
    "load_ai_settings",
]
