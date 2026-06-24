"""Message data access — implements `MessageRepository`.

Messages carry `user_id` (denormalized), so history reads filter on it directly — a user can only
read their own messages even if they pass someone else's `conversation_id` (defense in depth on
top of the conversation ownership check at the endpoint).
"""
from __future__ import annotations

from api._core.db import connect
from api._core.models import MESSAGE_COLUMNS, Message


class PostgresMessageRepository:
    def add(
        self,
        conversation_id: int,
        user_id: int,
        role: str,
        content: str,
        bubble_color: str | None = None,
        color_rule: str | None = None,
    ) -> Message:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                "insert into messages "
                "(conversation_id, user_id, role, content, bubble_color, color_rule) "
                f"values (%s, %s, %s, %s, %s, %s) returning {MESSAGE_COLUMNS}",
                (conversation_id, user_id, role, content, bubble_color, color_rule),
            )
            row = cur.fetchone()
            conn.commit()
        return Message.from_row(row)

    def list_for_conversation(self, conversation_id: int, user_id: int) -> list[Message]:
        """Conversation history, oldest first — scoped to the owner (isolation)."""
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                f"select {MESSAGE_COLUMNS} from messages "
                f"where conversation_id = %s and user_id = %s order by created_at asc, id asc",
                (conversation_id, user_id),
            )
            rows = cur.fetchall()
        return [Message.from_row(r) for r in rows]
