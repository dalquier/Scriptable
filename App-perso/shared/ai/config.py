"""Central OpenAI configuration shared by App-perso projects.

This module contains no secret value. The runtime must provide OPENAI_API_KEY
through Replit Secrets or another approved secret manager.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


class AIConfigurationError(RuntimeError):
    """Raised when required AI runtime configuration is missing."""


@dataclass(frozen=True)
class AISettings:
    api_key: str
    economy_model: str
    balanced_model: str
    reasoning_model: str
    coding_model: str
    embedding_model: str
    web_enabled: bool
    request_timeout_seconds: float
    max_retries: int


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_ai_settings() -> AISettings:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise AIConfigurationError(
            "OPENAI_API_KEY is missing. Add it to the runtime secret manager."
        )

    return AISettings(
        api_key=api_key,
        economy_model=os.getenv("OPENAI_MODEL_ECONOMY", "").strip(),
        balanced_model=os.getenv("OPENAI_MODEL_BALANCED", "").strip(),
        reasoning_model=os.getenv("OPENAI_MODEL_REASONING", "").strip(),
        coding_model=os.getenv("OPENAI_MODEL_CODING", "").strip(),
        embedding_model=os.getenv("OPENAI_MODEL_EMBEDDING", "").strip(),
        web_enabled=_env_bool("OPENAI_WEB_ENABLED", True),
        request_timeout_seconds=float(
            os.getenv("OPENAI_REQUEST_TIMEOUT_SECONDS", "60")
        ),
        max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "2")),
    )
