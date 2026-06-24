"""Groq-backed LLMClient using LangChain ChatGroq with structured output.

Isolated here so LangChain/pydantic are imported only when the concrete client is constructed
(the rest of the app depends on the stdlib `LLMClient` interface). Model: openai/gpt-oss-120b.
Reads GROQ_API_KEY from the environment unless an api_key is injected.
"""
from __future__ import annotations

import os

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from api._core.llm import MessageAnalysis

_MODEL = "openai/gpt-oss-120b"

_SYSTEM = (
    "You are PetaSight's chat assistant. For each user message, do two things:\n"
    "1) Write a concise, helpful reply.\n"
    "2) Extract signals from THIS message only:\n"
    "   - city: a city named in the message, else null;\n"
    "   - temperature_c: a temperature in Celsius associated with that city, else null;\n"
    "   - decimal_value: a standalone decimal number exactly as written (e.g. '42.37'), else null;\n"
    "   - panic: how urgent or panicked the message sounds, 0.0 (calm) to 1.0 (high panic).\n"
    "Use null when a signal is absent. Do not invent values."
)


class _AnalysisSchema(BaseModel):
    reply: str = Field(description="A concise, helpful reply to the user's message.")
    city: str | None = Field(default=None, description="A city named in the message, else null.")
    temperature_c: float | None = Field(
        default=None, description="Temperature in Celsius tied to the city, else null."
    )
    decimal_value: str | None = Field(
        default=None, description="A standalone decimal number as written, else null."
    )
    panic: float = Field(description="Urgency/panic from 0.0 (calm) to 1.0 (high panic).")


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class GroqLLMClient:
    """LLMClient backed by Groq (LangChain ChatGroq + structured output)."""

    def __init__(self, *, api_key: str | None = None, model: str = _MODEL, temperature: float = 0.3):
        kwargs: dict = {"model": model, "temperature": temperature}
        key = api_key or os.environ.get("GROQ_API_KEY")
        if key:
            kwargs["api_key"] = key
        self._structured = ChatGroq(**kwargs).with_structured_output(_AnalysisSchema)

    def analyze(self, message: str) -> MessageAnalysis:
        result: _AnalysisSchema = self._structured.invoke(
            [("system", _SYSTEM), ("human", message)]
        )
        return MessageAnalysis(
            reply=result.reply,
            city=result.city,
            temperature_c=result.temperature_c,
            decimal_value=result.decimal_value,
            panic=_clamp01(result.panic),
        )
