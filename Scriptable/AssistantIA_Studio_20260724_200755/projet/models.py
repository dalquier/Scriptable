"""Modèles de données simples pour AssistantIA Studio."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Message:
    role: str
    content: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            id=str(data.get("id") or uuid4()),
            role=str(data.get("role") or "user"),
            content=str(data.get("content") or ""),
            created_at=str(data.get("created_at") or utc_now_iso()),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass
class Conversation:
    title: str = "Nouvelle conversation"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    messages: List[Message] = field(default_factory=list)
    previous_response_id: Optional[str] = None

    def add_message(self, role: str, content: str, **metadata: Any) -> Message:
        message = Message(role=role, content=content, metadata=metadata)
        self.messages.append(message)
        self.updated_at = utc_now_iso()
        if self.title == "Nouvelle conversation" and role == "user":
            normalized = " ".join(content.strip().split())
            self.title = normalized[:60] or self.title
        return message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "previous_response_id": self.previous_response_id,
            "messages": [message.to_dict() for message in self.messages],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        return cls(
            id=str(data.get("id") or uuid4()),
            title=str(data.get("title") or "Nouvelle conversation"),
            created_at=str(data.get("created_at") or utc_now_iso()),
            updated_at=str(data.get("updated_at") or utc_now_iso()),
            previous_response_id=data.get("previous_response_id"),
            messages=[Message.from_dict(item) for item in data.get("messages", [])],
        )
