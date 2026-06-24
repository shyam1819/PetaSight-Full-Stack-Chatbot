"""Colour primitives for the bubble engine — pure, stdlib only.

A `Color` is an RGB triple with a hex serialization (what the backend stores in
`messages.bubble_color`). `ramp()` interpolates across ordered anchor stops and backs both the
3-stop temperature ramp and the panic ramp. (A corrected take on the `review/` module's `_lerp`,
with the interpolation factor clamped.)
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int

    def to_hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value into [low, high]."""
    return max(low, min(high, value))


def lerp(a: float, b: float, f: float) -> float:
    """Linear interpolation between two scalars."""
    return a + (b - a) * f


def lerp_color(a: Color, b: Color, f: float) -> Color:
    """Component-wise interpolation between two colours; f is clamped to [0, 1]."""
    f = clamp(f, 0.0, 1.0)
    return Color(
        round(lerp(a.r, b.r, f)),
        round(lerp(a.g, b.g, f)),
        round(lerp(a.b, b.b, f)),
    )


def ramp(stops: list[tuple[float, Color]], t: float) -> Color:
    """Interpolate a colour across ordered (position, colour) stops.

    `stops` must be sorted by position ascending (positions in [0, 1]); `t` is clamped to the
    stops' range. Used for the 3-stop temperature and panic ramps.
    """
    if not stops:
        raise ValueError("stops must not be empty")
    t = clamp(t, stops[0][0], stops[-1][0])
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if p0 <= t <= p1:
            span = p1 - p0
            local = 0.0 if span == 0 else (t - p0) / span
            return lerp_color(c0, c1, local)
    return stops[-1][1]
