"""GET /api/me — return the identity from the verified session cookie, or 401."""
from http.server import BaseHTTPRequestHandler

from api._core.auth_guard import require_user
from api._core.http_helpers import send_json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        user = require_user(self)
        if user is None:
            return  # require_user already sent 401/503
        send_json(self, 200, {"user": {"id": user["sub"], "email": user["email"]}})
