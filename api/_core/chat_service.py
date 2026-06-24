"""Chat service — composes the LLM analysis + colour resolver, and orchestrates a persisted turn.

`build_reply` is the pure compute (analyze → resolve). `send_message` is the orchestration:
verify conversation ownership, then store the user message and the coloured assistant reply.
Depends only on the `LLMClient` + repository *interfaces* (DI), so it imports no psycopg/langchain
and unit-tests with fakes. Ownership is checked here; the endpoint (5.4) supplies `user_id` from
the verified cookie.
"""
from __future__ import annotations

from dataclasses import dataclass

from api._core.bubble_rules import resolve_bubble_color
from api._core.llm import LLMClient, MessageAnalysis
from api._core.models import Message
from api._core.repositories import ConversationRepository, MessageRepository


@dataclass(frozen=True)
class AssistantReply:
    reply: str
    bubble_color: str   # hex colour for the reply bubble (persisted)
    rule: str           # which rule decided the colour — provenance
    analysis: MessageAnalysis


@dataclass(frozen=True)
class SentTurn:
    user_message: Message
    assistant_message: Message


class ChatService:
    def __init__(
        self,
        llm: LLMClient,
        conversations: ConversationRepository,
        messages: MessageRepository,
    ):
        self._llm = llm
        self._conversations = conversations
        self._messages = messages

    def build_reply(self, user_message: str) -> AssistantReply:
        """One LLM round-trip → reply + signals; the resolver decides the bubble colour."""
        analysis = self._llm.analyze(user_message)
        bubble = resolve_bubble_color(user_message, analysis)
        return AssistantReply(
            reply=analysis.reply,
            bubble_color=bubble.color.to_hex(),
            rule=bubble.rule,
            analysis=analysis,
        )

    def send_message(self, conversation_id: int, user_id: int, text: str) -> SentTurn | None:
        """Persist a turn. Returns None if the conversation isn't owned by user_id (→ 404)."""
        if self._conversations.get(conversation_id, user_id) is None:
            return None  # not found / not owned — never leak another user's conversation

        # Compute first: if the LLM call fails, nothing is written (no dangling half-turn).
        reply = self.build_reply(text)
        user_message = self._messages.add(conversation_id, user_id, "user", text)
        assistant_message = self._messages.add(
            conversation_id,
            user_id,
            "assistant",
            reply.reply,
            bubble_color=reply.bubble_color,
            color_rule=reply.rule,
        )
        return SentTurn(user_message=user_message, assistant_message=assistant_message)
