"""Central OpenAI configuration shared by App-perso projects.

This module contains no secret value. The runtime must provide OPENAI_API_KEY
through Replit Secrets or another approved secret manager.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


class AIConfigurationError(RuntimeError):
    """Raised when required AI runtime configuration is missing or invalid."""


_ALLOWED_REASONING_EFFORTS = {"none", "low", "medium", "high", "xhigh", "max"}


@dataclass(frozen=True)
class AISettings:
    api_key: str
    economy_model: str
    balanced_model: str
    reasoning_model: str
    coding_model: str
    embedding_model: str
    economy_reasoning: str
    balanced_reasoning: str
    reasoning_reasoning: str
    coding_reasoning: str
    web_enabled: bool
    request_timeout_seconds: float
    max_retries: int


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _reasoning_effort(name: str, default: str) -> str:
    value = os.getenv(name, default).strip().lower()
    if value not in _ALLOWED_REASONING_EFFORTS:
        allowed = ", ".join(sorted(_ALLOWED_REASONING_EFFORTS))
        raise AIConfigurationError(f"{name} must be one of: {allowed}")
    return value


def load_ai_settings() -> AISettings:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise AIConfigurationError(
            "OPENAI_API_KEY is missing. Add it to the runtime secret manager."
        )

    return AISettings(
        api_key=api_key,
        economy_model=os.getenv("OPENAI_MODEL_ECONOMY", "gpt-5.6-luna").strip(),
        balanced_model=os.getenv("OPENAI_MODEL_BALANCED", "gpt-5.6-terra").strip(),
        reasoning_model=os.getenv("OPENAI_MODEL_REASONING", "gpt-5.6-sol").strip(),
        coding_model=os.getenv("OPENAI_MODEL_CODING", "gpt-5.6-sol").strip(),
        embedding_model=os.getenv(
            "OPENAI_MODEL_EMBEDDING", "text-embedding-3-small"
        ).strip(),
        economy_reasoning=_reasoning_effort("OPENAI_REASONING_ECONOMY", "none"),
        balanced_reasoning=_reasoning_effort("OPENAI_REASONING_BALANCED", "low"),
        reasoning_reasoning=_reasoning_effort(
            "OPENAI_REASONING_REASONING", "medium"
        ),
        coding_reasoning=_reasoning_effort("OPENAI_REASONING_CODING", "high"),
        web_enabled=_env_bool("OPENAI_WEB_ENABLED", True),
        request_timeout_seconds=float(
            os.getenv("OPENAI_REQUEST_TIMEOUT_SECONDS", "60")
        ),
        max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "2")),
    )
