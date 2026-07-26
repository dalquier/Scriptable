"""Typed configuration loading with deterministic precedence."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping

from .errors import ConfigurationError


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated settings used by the BUILD-1 kernel."""

    app_name: str = "DeveloperOS"
    environment: str = "development"
    log_level: str = "INFO"
    health_enabled: bool = True

    def validate(self) -> "Settings":
        """Validate values and return this immutable settings object."""

        if not self.app_name.strip():
            raise ConfigurationError("app_name must not be empty")
        if self.environment not in {"development", "test", "production"}:
            raise ConfigurationError(
                "environment must be one of: development, test, production"
            )
        if self.log_level.upper() not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ConfigurationError("log_level is invalid")
        return replace(self, log_level=self.log_level.upper())


def load_settings(
    path: str | Path | None = None,
    *,
    env: Mapping[str, str] | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> Settings:
    """Load settings using defaults < TOML < environment < explicit overrides."""

    values: dict[str, Any] = {}
    if path is not None:
        file_path = Path(path)
        if file_path.exists():
            try:
                with file_path.open("rb") as handle:
                    raw = tomllib.load(handle)
            except (OSError, tomllib.TOMLDecodeError) as exc:
                raise ConfigurationError(f"Cannot read configuration: {file_path}") from exc
            section = raw.get("developeros", raw)
            if not isinstance(section, dict):
                raise ConfigurationError("Configuration root must be a TOML table")
            values.update(section)

    source = os.environ if env is None else env
    mapping = {
        "DEVELOPEROS_APP_NAME": "app_name",
        "DEVELOPEROS_ENVIRONMENT": "environment",
        "DEVELOPEROS_LOG_LEVEL": "log_level",
        "DEVELOPEROS_HEALTH_ENABLED": "health_enabled",
    }
    for variable, key in mapping.items():
        if variable in source:
            values[key] = source[variable]

    if overrides:
        values.update(overrides)

    allowed = {field.name for field in Settings.__dataclass_fields__.values()}
    unknown = sorted(set(values) - allowed)
    if unknown:
        raise ConfigurationError(f"Unknown configuration keys: {', '.join(unknown)}")
    if "health_enabled" in values:
        values["health_enabled"] = _parse_bool(values["health_enabled"])
    try:
        return Settings(**values).validate()
    except TypeError as exc:
        raise ConfigurationError(f"Invalid configuration value types: {exc}") from exc


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    raise ConfigurationError(f"Expected a boolean value, got: {value!r}")
