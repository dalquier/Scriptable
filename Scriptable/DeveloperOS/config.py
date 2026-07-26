from dataclasses import dataclass
import json
import os
from pathlib import Path


@dataclass
class Config:
    model: str = "gpt-5.6"
    max_iterations: int = 20
    timeout_seconds: int = 120
    api_key_env: str = "OPENAI_API_KEY"

    @classmethod
    def load(cls, path: str = "config.json") -> "Config":
        file_path = Path(path)
        if not file_path.exists():
            return cls()
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return cls(**{k: data[k] for k in data if k in cls.__annotations__})

    def api_key(self) -> str:
        key = os.environ.get(self.api_key_env, "").strip()
        if not key:
            raise RuntimeError(f"Variable {self.api_key_env} absente")
        return key
