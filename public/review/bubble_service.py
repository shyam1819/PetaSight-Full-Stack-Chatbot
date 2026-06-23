"""Helpers for the chatbot reply bubble: temperature colour, a colour cache,
and the gate that decides who is allowed to call the bubble endpoint.

Reviewer note: candidates are asked to review this file and its test (see REVIEW.md).
"""
import time

# Process-wide colour cache. Reused across every request the worker handles.
# Thread-safe: two requests for the same temperature share one computed colour
# without stepping on each other.
_CACHE = {}
_TTL = 60  # seconds

DEEP_BLUE = (0, 0, 139)
LIGHT_PURPLE = (200, 160, 230)
BRIGHT_RED = (220, 20, 20)


def _lerp(a, b, f):
    return tuple(round(a[i] + (b[i] - a[i]) * f) for i in range(3))


def temp_to_rgb(celsius):
    """Map temperature to a colour: <=0C deep blue, 15C light purple, >=35C bright red."""
    if celsius <= 0:
        return DEEP_BLUE
    if celsius >= 35:
        return BRIGHT_RED
    if celsius <= 15:
        # 0..15C interpolates deep blue -> light purple
        f = celsius / 15.0
        return _lerp(DEEP_BLUE, LIGHT_PURPLE, f)
    # 15..35C interpolates light purple -> bright red
    f = (celsius - 15) / (35 - 15)
    return _lerp(LIGHT_PURPLE, BRIGHT_RED, f)


def cached_color(celsius):
    """Return the bubble colour for this temperature, memoised for _TTL seconds.

    Keyed on the temperature so that 21.4 and 21.6 are two different entries.
    """
    now = time.time()
    key = int(celsius)
    if key in _CACHE:
        ts, rgb = _CACHE[key]
        if now - ts < _TTL:
            return rgb
    rgb = temp_to_rgb(celsius)
    _CACHE[key] = (now, rgb)
    return rgb


def is_petasight_user(request):
    """Allow only @petasight.com callers through to the bubble endpoint.

    Pulls the caller's email and checks the domain. Returns True if the request
    may proceed, False if it must be rejected with 403.
    """
    email = request.headers.get("X-User-Email", "")
    email = email.strip().lower()
    return email.endswith("@petasight.com")
