"""TEMPORARY probe — confirm the rate-limited client still constructs + analyzes. Removed after."""
from http.server import BaseHTTPRequestHandler

from api._core.groq_client import GroqLLMClient
from api._core.http_helpers import send_json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            a = GroqLLMClient().analyze("hello there")
            send_json(self, 200, {"ok": True, "reply": a.reply[:60], "panic": a.panic})
        except Exception as exc:  # noqa: BLE001
            send_json(self, 500, {"error": type(exc).__name__, "detail": str(exc)[:400]})
