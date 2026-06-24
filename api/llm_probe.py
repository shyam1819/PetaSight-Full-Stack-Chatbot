"""TEMPORARY probe — verify the 3-level panic enum across samples. Removed after."""
from http.server import BaseHTTPRequestHandler

from api._core.groq_client import GroqLLMClient
from api._core.http_helpers import send_json

_SAMPLES = [
    "Austin 21.5 we need to leave right now",
    "just checking in, all good here :)",
    "the total came to 42.37",
]


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            client = GroqLLMClient()
            out = []
            for s in _SAMPLES:
                a = client.analyze(s)
                out.append(
                    {
                        "input": s,
                        "city": a.city,
                        "temperature_c": a.temperature_c,
                        "decimal_value": a.decimal_value,
                        "panic": a.panic,
                    }
                )
            send_json(self, 200, {"results": out})
        except Exception as exc:  # noqa: BLE001
            send_json(self, 500, {"error": type(exc).__name__, "detail": str(exc)[:400]})
