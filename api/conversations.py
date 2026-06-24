"""/api/conversations — list (GET) and create (POST) the signed-in user's conversations.

user_id comes ONLY from the verified session cookie (require_user); the client never supplies it.
"""
from http.server import BaseHTTPRequestHandler

from api._core.auth_guard import require_user
from api._core.conversations_repo import PostgresConversationRepository
from api._core.http_helpers import read_json, send_json


def _convo_dict(c) -> dict:
    return {"id": c.id, "title": c.title, "created_at": c.created_at.isoformat()}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        user = require_user(self)
        if user is None:
            return
        convos = PostgresConversationRepository().list_by_user(user["sub"])
        send_json(self, 200, {"conversations": [_convo_dict(c) for c in convos]})

    def do_POST(self):
        user = require_user(self)
        if user is None:
            return
        title = read_json(self).get("title") or None
        convo = PostgresConversationRepository().create(user["sub"], title)
        send_json(self, 201, {"conversation": _convo_dict(convo)})
