"""LLM abstraction — interface + domain result, stdlib-only.

The result is a plain dataclass (not Pydantic) so the color engine and its tests depend on this
without pulling in LangChain/pydantic. The concrete Groq client lives in `groq_client.py`.

The single `analyze()` call is the "parallel agent": one inference returns the reply plus the
signals for all three colour conditions. Code stays authoritative — it validates the decimal and
owns the rule precedence/collision (EP-3).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

# Panic is the LLM's subjective judgment, so it's an ordinal *category* (reliable, reproducible)
# rather than a false-precision float. Code maps it onto the violet→magenta→yellow ramp (EP-3):
# calm → pale yellow, neutral → magenta, panicked → violet.
PanicLevel = Literal["calm", "neutral", "panicked"]


@dataclass(frozen=True)
class MessageAnalysis:
    reply: str
    city: str | None
    temperature_c: float | None
    decimal_value: str | None  # as written by the model, e.g. "42.37"; code re-validates it
    panic: PanicLevel


# Prior turns as (role, content) pairs, role in {"user", "assistant"} — used for the REPLY only.
History = list[tuple[str, str]]


class LLMClient(Protocol):
    def analyze(self, message: str, history: History | None = None) -> MessageAnalysis: ...
