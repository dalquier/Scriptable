from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Conversation:
    id: str
    title: str
    status: str
    created_at: str
    updated_at: str
    last_message_preview: str = ""
    message_count: int = 0


@dataclass(frozen=True)
class Message:
    id: str
    conversation_id: str
    sequence: int
    role: str
    content: str
    status: str
    request_id: Optional[str]
    created_at: str
