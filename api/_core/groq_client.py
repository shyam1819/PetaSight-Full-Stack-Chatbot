"""Groq-backed LLMClient using a LangGraph fan-out: reply + classify run in parallel.

A single ChatGroq instance backs both nodes — the `reply` node invokes it directly, the `classify`
node wraps it with `.with_structured_output()`. Both nodes branch from START and run concurrently
(LangGraph runs same-super-step nodes in parallel), then join, so reply + signals are produced
simultaneously and we wait for both.

`get_groq_client()` is a lazily-initialized, process-wide singleton: the model + compiled graph are
built once per warm instance and reused across requests, all paced by one shared rate limiter.
Isolated here so LangChain/LangGraph/pydantic load only when this concrete client is constructed;
the rest of the app depends on the stdlib `LLMClient` interface. Model: openai/gpt-oss-120b.
"""
from __future__ import annotations

import os
from typing import Literal, TypedDict

from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from api._core.llm import MessageAnalysis

_MODEL = "openai/gpt-oss-120b"

# Module-level so it persists across requests on a warm instance (per-instance only in serverless
# — see DECISIONS 4.3). Shared by every call → 20 calls/min is a combined cap.
_RATE_LIMITER = InMemoryRateLimiter(
    requests_per_second=20 / 60,   # 20 requests per minute
    check_every_n_seconds=0.1,     # poll the bucket every 100ms
    max_bucket_size=20,            # allow a burst of up to 20
)

REPLY_SYSTEM = "You are PetaSight's chat assistant. Write a concise, helpful reply to the user's message."

CLASSIFY_SYSTEM = (
    "Extract signals from the user's message (THIS message only):\n"
    "- city: a city named in the message, else null;\n"
    "- temperature_c: a temperature in Celsius — ONLY if the message gives the number with a unit "
    "(°C, C, 'degrees', 'Celsius') or explicitly describes it as a temperature. A bare number next "
    "to a city (e.g. 'Austin 21.5') is NOT a temperature → null;\n"
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
    history: list  # prior (role, content) turns — reply context only
    reply: str
    signals: _Signals


class GroqLLMClient:
    """LLMClient backed by Groq; one model drives both parallel LangGraph nodes."""

    def __init__(self, *, api_key: str | None = None, model: str = _MODEL, temperature: float = 0.3):
        kwargs: dict = {"model": model, "temperature": temperature, "rate_limiter": _RATE_LIMITER}
        key = api_key or os.environ.get("GROQ_API_KEY")
        if key:
            kwargs["api_key"] = key
        self._model = ChatGroq(**kwargs)                       # single instance for both nodes
        self._classifier = self._model.with_structured_output(_Signals)
        self._graph = self._build_graph()

    def _build_graph(self):
        def reply_node(state: _State) -> dict:
            # Reply uses the conversation history for context.
            msgs: list = [("system", REPLY_SYSTEM)]
            for role, content in state.get("history") or []:
                msgs.append(("ai" if role == "assistant" else "human", content))
            msgs.append(("human", state["message"]))
            return {"reply": self._model.invoke(msgs).content}

        def classify_node(state: _State) -> dict:
            # Classification (colour) is per-message — deliberately ignores history.
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

    def analyze(self, message: str, history: list | None = None) -> MessageAnalysis:
        final = self._graph.invoke({"message": message, "history": history or []})
        signals: _Signals = final["signals"]
        return MessageAnalysis(
            reply=final["reply"],
            city=signals.city,
            temperature_c=signals.temperature_c,
            decimal_value=signals.decimal_value,
            panic=signals.panic,
        )


_instance: GroqLLMClient | None = None


def get_groq_client() -> GroqLLMClient:
    """Process-wide singleton (lazy): one model + graph per warm instance, reused across requests."""
    global _instance
    if _instance is None:
        _instance = GroqLLMClient()
    return _instance
