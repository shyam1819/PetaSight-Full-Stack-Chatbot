"""Domain models — plain data, no DB or framework coupling."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

# Column order shared with the repositories' SELECT/RETURNING clauses.
USER_COLUMNS = "id, email, password_hash, created_at"


@dataclass(frozen=True)
class User:
    id: int
    email: str
    password_hash: str
    created_at: datetime

    @classmethod
    def from_row(cls, row) -> "User":
        """Map a DB row (in USER_COLUMNS order) to a User."""
        return cls(id=row[0], email=row[1], password_hash=row[2], created_at=row[3])


CONVERSATION_COLUMNS = "id, user_id, title, created_at"


@dataclass(frozen=True)
class Conversation:
    id: int
    user_id: int
    title: str | None
    created_at: datetime

    @classmethod
    def from_row(cls, row) -> "Conversation":
        """Map a DB row (in CONVERSATION_COLUMNS order) to a Conversation."""
        return cls(id=row[0], user_id=row[1], title=row[2], created_at=row[3])


MESSAGE_COLUMNS = "id, conversation_id, user_id, role, content, bubble_color, color_rule, created_at"


@dataclass(frozen=True)
class Message:
    id: int
    conversation_id: int
    user_id: int
    role: str  # 'user' | 'assistant'
    content: str
    bubble_color: str | None  # hex; set on assistant messages
    color_rule: str | None    # which rule decided the colour (provenance)
    created_at: datetime

    @classmethod
    def from_row(cls, row) -> "Message":
        """Map a DB row (in MESSAGE_COLUMNS order) to a Message."""
        return cls(
            id=row[0],
            conversation_id=row[1],
            user_id=row[2],
            role=row[3],
            content=row[4],
            bubble_color=row[5],
            color_rule=row[6],
            created_at=row[7],
        )
