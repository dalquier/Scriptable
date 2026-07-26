import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List


@dataclass
class State:
    iteration: int = 0
    status: str = "idle"
    last_response: str = ""
    history: List[str] = None

    def __post_init__(self) -> None:
        if self.history is None:
            self.history = []


class StateStore:
    def __init__(self, path: str = "state.json") -> None:
        self.path = Path(path)

    def load(self) -> State:
        if not self.path.exists():
            return State()
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return State(**data)

    def save(self, state: State) -> None:
        self.path.write_text(
            json.dumps(asdict(state), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
