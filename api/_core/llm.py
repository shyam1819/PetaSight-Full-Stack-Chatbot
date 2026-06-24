"""LLM abstraction — interface + domain result, stdlib-only.

The result is a plain dataclass (not Pydantic) so the color engine and its tests depend on this
without pulling in LangChain/pydantic. The concrete Groq client lives in `groq_client.py`.

The single `analyze()` call is the "parallel agent": one inference returns the reply plus the
signals for all three colour conditions. Code stays authoritative — it validates the decimal and
owns the rule precedence/collision (EP-3).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class MessageAnalysis:
    reply: str
    city: str | None
    temperature_c: float | None
    decimal_value: str | None  # as written by the model, e.g. "42.37"; code re-validates it
    panic: float  # 0.0 calm .. 1.0 high panic


class LLMClient(Protocol):
    def analyze(self, message: str) -> MessageAnalysis: ...
