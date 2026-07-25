"""Configuration de Dev Autopilot lue depuis les variables d'environnement."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    github_token: str
    openai_model: str
    github_repository: str
    github_branch: str
    target_root: str
    max_iterations: int
    timeout_seconds: int


def load_settings() -> Settings:
    settings = Settings(
        openai_api_key=os.environ.get("OPENAI_API_KEY", "").strip(),
        github_token=os.environ.get("GITHUB_TOKEN", "").strip(),
        openai_model=os.environ.get("OPENAI_MODEL", "gpt-5.6").strip(),
        github_repository=os.environ.get("GITHUB_REPOSITORY", "dalquier/Scriptable").strip(),
        github_branch=os.environ.get("GITHUB_BRANCH", "main").strip(),
        target_root=os.environ.get("TARGET_ROOT", "Scriptable/Generated_Project").strip().strip("/"),
        max_iterations=int(os.environ.get("MAX_ITERATIONS", "30")),
        timeout_seconds=int(os.environ.get("TIMEOUT_SECONDS", "180")),
    )

    missing = []
    if not settings.openai_api_key:
        missing.append("OPENAI_API_KEY")
    if not settings.github_token:
        missing.append("GITHUB_TOKEN")
    if missing:
        raise RuntimeError(
            "Variables d'environnement manquantes : " + ", ".join(missing)
        )
    if settings.max_iterations < 1:
        raise RuntimeError("MAX_ITERATIONS doit être supérieur ou égal à 1.")
    return settings
