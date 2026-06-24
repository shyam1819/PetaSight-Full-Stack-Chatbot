"""GET /api/me — return the identity from the verified session cookie, or 401."""
from http.server import BaseHTTPRequestHandler

from api._core.http_helpers import send_json
from api._core.sessions import SessionError, read_token_from_cookies, verify


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        token = read_token_from_cookies(self.headers.get("Cookie"))
        try:
            payload = verify(token) if token else None
        except SessionError:
            return send_json(self, 503, {"message": "Server not configured."})

        if not payload:
            return send_json(self, 401, {"message": "Not authenticated."})
        return send_json(self, 200, {"user": {"id": payload["sub"], "email": payload["email"]}})
