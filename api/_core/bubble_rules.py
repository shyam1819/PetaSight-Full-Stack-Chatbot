"""Bubble colour rules — pure functions over the LLM signals + the original message.

Each rule has the uniform signature `(message, analysis) -> Color | None`: it returns a colour
when it applies, else None. The resolver (story 3.5) chains them first-match-wins. Colours are
decided server-side and stored (DECISIONS EP-3); text contrast is the frontend's job.

Anchors reuse the provided review/ module's temperature colours.
"""
from __future__ import annotations

from api._core.colors import Color, ramp
from api._core.llm import MessageAnalysis

# Rule 1 — temperature ramp (°C). Clamped deep blue ≤0 → light purple 15 → bright red ≥35.
DEEP_BLUE = Color(0, 0, 139)
LIGHT_PURPLE = Color(200, 160, 230)
BRIGHT_RED = Color(220, 20, 20)
_TEMP_STOPS: list[tuple[float, Color]] = [
    (0.0, DEEP_BLUE),
    (15.0, LIGHT_PURPLE),
    (35.0, BRIGHT_RED),
]


def temperature_color(celsius: float) -> Color:
    """Map a temperature (°C) to its bubble colour; clamped outside 0–35 (ramp handles it)."""
    return ramp(_TEMP_STOPS, celsius)


def temperature_rule(message: str, analysis: MessageAnalysis) -> Color | None:
    """Rule 1: applies only when the message has BOTH a city and a temperature."""
    if analysis.city and analysis.temperature_c is not None:
        return temperature_color(analysis.temperature_c)
    return None
