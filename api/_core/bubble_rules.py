"""Bubble colour rules — pure functions over the LLM signals + the original message.

Each rule has the uniform signature `(message, analysis) -> Color | None`: it returns a colour
when it applies, else None. The resolver (story 3.5) chains them first-match-wins. Colours are
decided server-side and stored (DECISIONS EP-3); text contrast is the frontend's job.

Anchors reuse the provided review/ module's temperature colours.
"""
from __future__ import annotations

import re

from api._core.colors import Color, lerp_color, ramp
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


# Rule 2 — standalone decimal → grayscale by the first two fractional digits (.00 light, .99 dark).
DECIMAL_LIGHTEST = Color(0xEC, 0xEA, 0xE3)  # .00
DECIMAL_DARKEST = Color(0x1C, 0x1C, 0x1C)   # .99

# A decimal token with an integer part, NOT adjacent to other word chars or dots — so version
# strings ("1.2.3") and IPs ("192.168.0.1") don't match.
_DECIMAL_RE = re.compile(r"(?<![\w.])\d+\.\d+(?![\w.])")


def extract_standalone_decimal(message: str) -> str | None:
    """Find the first standalone decimal in the message. Code-authoritative (not the LLM's value)."""
    match = _DECIMAL_RE.search(message or "")
    return match.group(0) if match else None


def _first_two_fractional_digits(decimal: str) -> int:
    """'42.37' -> 37, '0.5' -> 50 (right-padded), '3.0' -> 0."""
    fractional = decimal.split(".")[1]
    return int((fractional + "00")[:2])


def decimal_color(first_two_digits: int) -> Color:
    """Map the first two fractional digits (0–99) to the grayscale ramp."""
    return lerp_color(DECIMAL_LIGHTEST, DECIMAL_DARKEST, first_two_digits / 99)


def decimal_rule(message: str, analysis: MessageAnalysis) -> Color | None:
    """Rule 2: a standalone decimal in the message — code's regex is authoritative (the LLM's
    `decimal_value` is only a cross-check, never trusted for the exact digits)."""
    decimal = extract_standalone_decimal(message)
    if decimal is None:
        return None
    return decimal_color(_first_two_fractional_digits(decimal))


# Rule 3 — panic (LLM-classified 3-level enum). calm → pale yellow, neutral → magenta,
# panicked → violet. Discrete categories map straight to the brief's three named colours.
PANIC_PALE_YELLOW = Color(0xF4, 0xED, 0xA6)  # calm
PANIC_MAGENTA = Color(0xD6, 0x21, 0x9B)      # neutral
PANIC_VIOLET = Color(0x7A, 0x1F, 0xA2)       # panicked

_PANIC_COLORS = {
    "calm": PANIC_PALE_YELLOW,
    "neutral": PANIC_MAGENTA,
    "panicked": PANIC_VIOLET,
}


def panic_color(level: str) -> Color:
    """Map the 3-level panic category to its colour (defensive default: neutral/magenta)."""
    return _PANIC_COLORS.get(level, PANIC_MAGENTA)


def panic_rule(message: str, analysis: MessageAnalysis) -> Color:
    """Rule 3: the fallback — always matches, colouring by the LLM's panic category."""
    return panic_color(analysis.panic)
