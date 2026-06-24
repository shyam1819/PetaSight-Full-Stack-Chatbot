"""TEMPORARY probe — verify the temperature-needs-a-unit rule end to end. Removed after."""
from http.server import BaseHTTPRequestHandler

from api._core.bubble_rules import resolve_bubble_color
from api._core.groq_client import get_groq_client
from api._core.http_helpers import send_json

_SAMPLES = [
    "Austin 21.5 we need to leave right now",   # bare number -> NOT temp -> decimal
    "Austin 21.5C, we need to leave now",        # unit -> temperature
    "it's 21.5 degrees in Austin",               # described as temperature -> temperature
    "the score is 21.5",                         # no city, no unit -> decimal
]


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            client = get_groq_client()
            out = []
            for s in _SAMPLES:
                a = client.analyze(s)
                r = resolve_bubble_color(s, a)
                out.append(
                    {
                        "input": s,
                        "city": a.city,
                        "temperature_c": a.temperature_c,
                        "decimal_value": a.decimal_value,
                        "panic": a.panic,
                        "rule": r.rule,
                        "color": r.color.to_hex(),
                    }
                )
            send_json(self, 200, {"results": out})
        except Exception as exc:  # noqa: BLE001
            send_json(self, 500, {"error": type(exc).__name__, "detail": str(exc)[:400]})
