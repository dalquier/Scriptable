from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AgentConfig:
    repository: str
    base_branch: str
    working_branch_prefix: str
    project_path: str
    state_file: str
    mission_file: str
    model: str
    api_url: str
    max_output_tokens: int
    max_iterations_per_run: int
    max_repair_attempts: int
    test_commands: tuple[str, ...]
    auto_push: bool
    auto_open_pr: bool
    dry_run: bool


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_config(root: Path) -> AgentConfig:
    config_path = root / "settings.json"
    if not config_path.exists():
        config_path = root / "settings.example.json"
    data = _read_json(config_path)

    return AgentConfig(
        repository=str(data["repository"]),
        base_branch=str(data.get("base_branch", "main")),
        working_branch_prefix=str(data.get("working_branch_prefix", "developeros/agent")),
        project_path=str(data.get("project_path", "Scriptable/DeveloperOS")),
        state_file=str(data.get("state_file", "state.json")),
        mission_file=str(data.get("mission_file", "MISSION.md")),
        model=str(data.get("model", os.getenv("OPENAI_MODEL", "gpt-5.6"))),
        api_url=str(data.get("api_url", "https://api.openai.com/v1/responses")),
        max_output_tokens=int(data.get("max_output_tokens", 12000)),
        max_iterations_per_run=int(data.get("max_iterations_per_run", 5)),
        max_repair_attempts=int(data.get("max_repair_attempts", 3)),
        test_commands=tuple(str(v) for v in data.get("test_commands", ["python -m compileall .", "python -m unittest discover -s tests -v"])),
        auto_push=bool(data.get("auto_push", True)),
        auto_open_pr=bool(data.get("auto_open_pr", True)),
        dry_run=bool(data.get("dry_run", False)),
    )
