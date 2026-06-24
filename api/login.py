"""Login stub for Task 1 — pipeline + integration check only.

Enforces the @petasight.com domain gate at the backend (not just the UI), but
does NOT do real auth, sessions, or DB work yet. That lands in Task 3.
"""
from http.server import BaseHTTPRequestHandler
import json

ALLOWED_DOMAIN = "@petasight.com"


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            data = {}

        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))

        if not email or not password:
            return self._send(400, {"message": "Email and password are required."})
        if not email.endswith(ALLOWED_DOMAIN):
            return self._send(403, {"message": "Only @petasight.com accounts are allowed."})

        return self._send(200, {"message": f"Pipeline OK — {email} accepted."})

    def _send(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)
