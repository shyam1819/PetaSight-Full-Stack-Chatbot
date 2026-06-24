"""TEMPORARY probe — verify LangGraph parallel analyze + show it's concurrent. Removed after."""
import time
from http.server import BaseHTTPRequestHandler

from api._core.groq_client import CLASSIFY_SYSTEM, REPLY_SYSTEM, GroqLLMClient
from api._core.http_helpers import send_json

_SAMPLE = "Austin 21.5 we need to leave right now"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            client = GroqLLMClient()

            t0 = time.time()
            a = client.analyze(_SAMPLE)
            parallel_s = round(time.time() - t0, 2)

            # Sequential baseline: same two calls back to back.
            t0 = time.time()
            client._chat.invoke([("system", REPLY_SYSTEM), ("human", _SAMPLE)])
            client._classifier.invoke([("system", CLASSIFY_SYSTEM), ("human", _SAMPLE)])
            sequential_s = round(time.time() - t0, 2)

            send_json(
                self,
                200,
                {
                    "parallel_s": parallel_s,
                    "sequential_s": sequential_s,
                    "analysis": {
                        "reply": a.reply[:80],
                        "city": a.city,
                        "temperature_c": a.temperature_c,
                        "decimal_value": a.decimal_value,
                        "panic": a.panic,
                    },
                },
            )
        except Exception as exc:  # noqa: BLE001
            send_json(self, 500, {"error": type(exc).__name__, "detail": str(exc)[:400]})
