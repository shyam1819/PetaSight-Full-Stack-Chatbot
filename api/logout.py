"""POST /api/logout — clear the session cookie. Stateless and idempotent."""
from http.server import BaseHTTPRequestHandler

from api._core.http_helpers import send_json
from api._core.sessions import clear_session_cookie


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        send_json(self, 200, {"message": "Logged out."}, {"Set-Cookie": clear_session_cookie()})
