"""Groq-backed LLMClient using a LangGraph fan-out: reply + classify run in parallel.

Two independent nodes branch from START and run concurrently (LangGraph executes same-super-step
nodes in parallel), then join — so the chat reply and the signal classification are produced
simultaneously and we wait for both. Each uses a focused prompt/temperature.

Isolated here so LangChain/LangGraph/pydantic load only when this concrete client is constructed;
the rest of the app depends on the stdlib `LLMClient` interface. Model: openai/gpt-oss-120b.
"""
from __future__ import annotations

import os
from typing import Literal, TypedDict

from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from api._core.llm import MessageAnalysis

_MODEL = "openai/gpt-oss-120b"

REPLY_SYSTEM = "You are PetaSight's chat assistant. Write a concise, helpful reply to the user's message."

CLASSIFY_SYSTEM = (
    "Extract signals from the user's message (THIS message only):\n"
    "- city: a city named in the message, else null;\n"
    "- temperature_c: a temperature in Celsius tied to that city, else null;\n"
    "- decimal_value: a standalone decimal number exactly as written (e.g. '42.37'), else null;\n"
    "- panic: classify how the message feels as exactly one of 'calm', 'neutral', or 'panicked'.\n"
    "Use null when a signal is absent. Do not invent values."
)


class _Signals(BaseModel):
    city: str | None = Field(default=None, description="A city named in the message, else null.")
    temperature_c: float | None = Field(
        default=None, description="Temperature in Celsius tied to the city, else null."
    )
    decimal_value: str | None = Field(
        default=None, description="A standalone decimal number as written, else null."
    )
    panic: Literal["calm", "neutral", "panicked"] = Field(
        description="How urgent the message feels: calm, neutral, or panicked."
    )


class _State(TypedDict):
    message: str
    reply: str
    signals: _Signals


class GroqLLMClient:
    """LLMClient backed by Groq, running reply + classify in parallel via LangGraph."""

    def __init__(self, *, api_key: str | None = None, model: str = _MODEL):
        common: dict = {"model": model}
        key = api_key or os.environ.get("GROQ_API_KEY")
        if key:
            common["api_key"] = key
        self._chat = ChatGroq(**common, temperature=0.5)
        self._classifier = ChatGroq(**common, temperature=0.0).with_structured_output(_Signals)
        self._graph = self._build_graph()

    def _build_graph(self):
        def reply_node(state: _State) -> dict:
            msg = self._chat.invoke([("system", REPLY_SYSTEM), ("human", state["message"])])
            return {"reply": msg.content}

        def classify_node(state: _State) -> dict:
            signals = self._classifier.invoke(
                [("system", CLASSIFY_SYSTEM), ("human", state["message"])]
            )
            return {"signals": signals}

        builder = StateGraph(_State)
        builder.add_node("reply", reply_node)
        builder.add_node("classify", classify_node)
        # Fan out from START -> both nodes run in the same super-step (concurrently), then join.
        builder.add_edge(START, "reply")
        builder.add_edge(START, "classify")
        builder.add_edge("reply", END)
        builder.add_edge("classify", END)
        return builder.compile()

    def analyze(self, message: str) -> MessageAnalysis:
        final = self._graph.invoke({"message": message})
        signals: _Signals = final["signals"]
        return MessageAnalysis(
            reply=final["reply"],
            city=signals.city,
            temperature_c=signals.temperature_c,
            decimal_value=signals.decimal_value,
            panic=signals.panic,
        )
