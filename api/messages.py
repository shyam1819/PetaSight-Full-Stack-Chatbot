"""/api/messages — conversation history (GET ?conversation_id=) and send a message (POST).

user_id comes ONLY from the verified session cookie. Ownership is enforced (404 for a conversation
that isn't yours), and the message repo additionally filters history by user_id.
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from api._core.auth_guard import require_user
from api._core.conversations_repo import PostgresConversationRepository
from api._core.http_helpers import read_json, send_json
from api._core.messages_repo import PostgresMessageRepository


def _msg_dict(m) -> dict:
    return {
        "id": m.id,
        "role": m.role,
        "content": m.content,
        "bubble_color": m.bubble_color,
        "color_rule": m.color_rule,
        "created_at": m.created_at.isoformat(),
    }


def _query_int(path: str, key: str):
    values = parse_qs(urlparse(path).query).get(key)
    if not values:
        return None
    try:
        return int(values[0])
    except ValueError:
        return None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        user = require_user(self)
        if user is None:
            return
        conversation_id = _query_int(self.path, "conversation_id")
        if conversation_id is None:
            return send_json(self, 400, {"message": "conversation_id is required."})
        if PostgresConversationRepository().get(conversation_id, user["sub"]) is None:
            return send_json(self, 404, {"message": "Conversation not found."})
        msgs = PostgresMessageRepository().list_for_conversation(conversation_id, user["sub"])
        send_json(self, 200, {"messages": [_msg_dict(m) for m in msgs]})

    def do_POST(self):
        user = require_user(self)
        if user is None:
            return
        data = read_json(self)
        conversation_id = data.get("conversation_id")
        text = (data.get("text") or "").strip()
        if not isinstance(conversation_id, int) or not text:
            return send_json(self, 400, {"message": "conversation_id and text are required."})

        # Lazy import so GET (history) doesn't pay the LangChain cold-start.
        from api._core.chat_service import ChatService
        from api._core.groq_client import get_groq_client

        chat = ChatService(
            get_groq_client(),
            PostgresConversationRepository(),
            PostgresMessageRepository(),
        )
        turn = chat.send_message(conversation_id, user["sub"], text)
        if turn is None:
            return send_json(self, 404, {"message": "Conversation not found."})
        send_json(
            self,
            201,
            {
                "user_message": _msg_dict(turn.user_message),
                "assistant_message": _msg_dict(turn.assistant_message),
            },
        )
