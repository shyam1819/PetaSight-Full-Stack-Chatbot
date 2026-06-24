"""Conversation data access — implements `ConversationRepository`.

Every query is scoped by `user_id`, so a user can only ever touch their own conversations.
`get()` is intentionally ownership-scoped (`WHERE id = %s AND user_id = %s`): a conversation that
isn't yours returns None, which is the core per-user isolation primitive (EP-5/THREATS).
"""
from __future__ import annotations

from api._core.db import connect
from api._core.models import CONVERSATION_COLUMNS, Conversation


class PostgresConversationRepository:
    def create(self, user_id: int, title: str | None = None) -> Conversation:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                f"insert into conversations (user_id, title) values (%s, %s) "
                f"returning {CONVERSATION_COLUMNS}",
                (user_id, title),
            )
            row = cur.fetchone()
            conn.commit()
        return Conversation.from_row(row)

    def list_by_user(self, user_id: int) -> list[Conversation]:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                f"select {CONVERSATION_COLUMNS} from conversations "
                f"where user_id = %s order by created_at desc, id desc",
                (user_id,),
            )
            rows = cur.fetchall()
        return [Conversation.from_row(r) for r in rows]

    def get(self, conversation_id: int, user_id: int) -> Conversation | None:
        """Return the conversation only if it belongs to user_id, else None (isolation)."""
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                f"select {CONVERSATION_COLUMNS} from conversations "
                f"where id = %s and user_id = %s",
                (conversation_id, user_id),
            )
            row = cur.fetchone()
        return Conversation.from_row(row) if row else None
