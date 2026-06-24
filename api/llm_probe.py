"""TEMPORARY probe (story 4.2) — verify GroqLLMClient.analyze on the real runtime. Removed after."""
from http.server import BaseHTTPRequestHandler

from api._core.groq_client import GroqLLMClient
from api._core.http_helpers import send_json

_SAMPLE = "Austin 21.5 we need to leave right now"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            analysis = GroqLLMClient().analyze(_SAMPLE)
            send_json(
                self,
                200,
                {
                    "input": _SAMPLE,
                    "reply": analysis.reply,
                    "city": analysis.city,
                    "temperature_c": analysis.temperature_c,
                    "decimal_value": analysis.decimal_value,
                    "panic": analysis.panic,
                },
            )
        except Exception as exc:  # noqa: BLE001
            send_json(self, 500, {"error": type(exc).__name__, "detail": str(exc)[:400]})
