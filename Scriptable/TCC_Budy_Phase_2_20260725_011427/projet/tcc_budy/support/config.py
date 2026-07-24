from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from tcc_budy.support.errors import ConfigurationError


DEFAULT_SYSTEM_INSTRUCTIONS = (
    "Tu es TCC Budy, un compagnon personnel de réflexion inspiré des TCC. "
    "Tu aides à clarifier les faits, pensées, émotions, sensations, impulsions, "
    "comportements et conséquences. Tu poses une question principale à la fois. "
    "Tu ne te présentes jamais comme psychologue, médecin ou service d’urgence, "
    "tu ne diagnostiques pas et tu ne modifies aucun traitement. En cas de danger "
    "immédiat plausible, tu encourages à contacter les secours ou un professionnel "
    "humain adapté."
)

DEFAULT_CONFIG = {
    "provider": "auto",
    "model": "gpt-5.5-mini",
    "api_url": "https://api.openai.com/v1/responses",
    "timeout_seconds": 90,
    "max_output_tokens": 1200,
    "context_message_limit": 12,
    "store_remote_responses": False,
    "system_instructions": DEFAULT_SYSTEM_INSTRUCTIONS,
}


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
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"JSON invalide dans {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError(f"{path.name} doit contenir un objet JSON.")
    return data


def _write_default_config(path: Path) -> None:
    try:
        path.write_text(
            json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise ConfigurationError(f"Impossible de créer {path.name}: {exc}") from exc


def load_settings(root: Path) -> Settings:
    root = Path(root)
    config_path = root / "config.json"
    secrets_path = root / "secrets.json"

    if not config_path.exists():
        _write_default_config(config_path)

    data = dict(DEFAULT_CONFIG)
    data.update(_read_json(config_path))

    secret_data = _read_json(secrets_path) if secrets_path.exists() else {}
    api_key = str(
        secret_data.get("OPENAI_API_KEY")
        or secret_data.get("api_key")
        or ""
    ).strip()
    secret_model = str(secret_data.get("OPENAI_MODEL") or "").strip()
    if secret_model:
        data["model"] = secret_model

    requested_provider = str(data.get("provider", "auto")).strip().lower()
    if requested_provider not in {"auto", "simulator", "openai"}:
        raise ConfigurationError(
            "provider doit valoir auto, simulator ou openai."
        )

    if requested_provider == "auto":
        provider = "openai" if api_key else "simulator"
    else:
        provider = requested_provider

    if provider == "openai" and not api_key:
        raise ConfigurationError(
            "OpenAI est activé mais aucune clé n'est présente dans secrets.json."
        )

    return Settings(
        provider=provider,
        model=str(data.get("model", DEFAULT_CONFIG["model"])).strip(),
        api_url=str(data.get("api_url", DEFAULT_CONFIG["api_url"])).strip(),
        timeout_seconds=max(10, int(data.get("timeout_seconds", 90))),
        max_output_tokens=max(128, int(data.get("max_output_tokens", 1200))),
        context_message_limit=max(2, int(data.get("context_message_limit", 12))),
        store_remote_responses=bool(data.get("store_remote_responses", False)),
        system_instructions=str(
            data.get("system_instructions", DEFAULT_SYSTEM_INSTRUCTIONS)
        ).strip(),
        api_key=api_key,
    )
