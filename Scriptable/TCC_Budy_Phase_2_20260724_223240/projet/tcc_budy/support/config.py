from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from tcc_budy.support.errors import ConfigurationError


@dataclass(frozen=True)
class Settings:
    provider: str
    model: str
    api_url: str
    timeout_seconds: int
    max_output_tokens: int
    context_message_limit: int
    store_remote_responses: bool
    system_instructions: str
    api_key: str

    @property
    def provider_label(self) -> str:
        return "OpenAI" if self.provider == "openai" else "Simulateur local"


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"JSON invalide dans {path.name}: {exc}") from exc


def load_settings(root: Path) -> Settings:
    root = Path(root)
    example = root / "config.example.json"
    config = root / "config.json"
    secrets = root / "secrets.json"

    if not example.exists():
        raise ConfigurationError("config.example.json est introuvable.")

    data = _read_json(example)
    if config.exists():
        data.update(_read_json(config))
    if secrets.exists():
        secret_data = _read_json(secrets)
        if "OPENAI_API_KEY" in secret_data:
            data["api_key"] = secret_data["OPENAI_API_KEY"]
        elif "api_key" in secret_data:
            data["api_key"] = secret_data["api_key"]

    provider = str(data.get("provider", "simulator")).strip().lower()
    if provider not in {"simulator", "openai"}:
        raise ConfigurationError("provider doit valoir simulator ou openai.")

    settings = Settings(
        provider=provider,
        model=str(data.get("model", "gpt-5.5-mini")).strip(),
        api_url=str(data.get("api_url", "https://api.openai.com/v1/responses")).strip(),
        timeout_seconds=max(10, int(data.get("timeout_seconds", 90))),
        max_output_tokens=max(128, int(data.get("max_output_tokens", 1200))),
        context_message_limit=max(2, int(data.get("context_message_limit", 12))),
        store_remote_responses=bool(data.get("store_remote_responses", False)),
        system_instructions=str(data.get("system_instructions", "")).strip(),
        api_key=str(data.get("api_key", "")).strip(),
    )
    if settings.provider == "openai" and not settings.api_key:
        raise ConfigurationError(
            "OpenAI est activé mais aucune clé n'est présente dans secrets.json."
        )
    return settings
