"""TEMPORARY probe — confirm singleton identity + single-instance analyze. Removed after."""
from http.server import BaseHTTPRequestHandler

from api._core.groq_client import get_groq_client
from api._core.http_helpers import send_json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            c1 = get_groq_client()
            c2 = get_groq_client()
            a = c1.analyze("Austin 21.5 we need to leave right now")
            send_json(
                self,
                200,
                {
                    "same_instance": c1 is c2,
                    "one_model_for_both_nodes": c1._classifier is not None and c1._model is not None,
                    "city": a.city,
                    "temperature_c": a.temperature_c,
                    "panic": a.panic,
                    "reply": a.reply[:60],
                },
            )
        except Exception as exc:  # noqa: BLE001
            send_json(self, 500, {"error": type(exc).__name__, "detail": str(exc)[:400]})
