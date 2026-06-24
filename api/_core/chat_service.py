"""Chat service — composes the LLM analysis and the colour resolver into a reply-with-colour.

Depends only on the `LLMClient` interface (DI) + the pure resolver, so it unit-tests with a fake
LLM and no DB/network. The DB persistence of the result (storing `bubble_color` on the message
row) lands in EP-5, where the conversation + message repository live.
"""
from __future__ import annotations

from dataclasses import dataclass

from api._core.bubble_rules import resolve_bubble_color
from api._core.llm import LLMClient, MessageAnalysis


@dataclass(frozen=True)
class AssistantReply:
    reply: str          # the assistant's text
    bubble_color: str   # hex colour for the reply bubble (what we persist)
    rule: str           # which rule decided the colour — provenance
    analysis: MessageAnalysis  # the signals — provenance


class ChatService:
    def __init__(self, llm: LLMClient):
        self._llm = llm

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
