from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Source:
    title: str
    url: str = ""
    snippet: str = ""
    source_type: str = "web"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    role: str
    content: str
    sources: List[Source] = field(default_factory=list)
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
            "sources": [source.__dict__ for source in self.sources],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        raw_sources = data.get("sources") or []
        sources = [Source(**item) for item in raw_sources if isinstance(item, dict)]
        return cls(
            role=str(data.get("role", "assistant")),
            content=str(data.get("content", "")),
            created_at=str(data.get("created_at", "")),
            sources=sources,
        )
