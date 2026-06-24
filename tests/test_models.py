"""Unit tests for domain models (story 2.3) — no DB needed."""
from datetime import datetime

from api._core.models import Conversation, Message, User


def test_user_from_row():
    created = datetime(2026, 1, 1, 12, 0, 0)
    user = User.from_row((1, "alice@petasight.com", "pbkdf2_sha256$1$a$b", created))
    assert user.id == 1
    assert user.email == "alice@petasight.com"
    assert user.password_hash == "pbkdf2_sha256$1$a$b"
    assert user.created_at == created


def test_user_is_frozen():
    user = User.from_row((1, "a@petasight.com", "h", datetime(2026, 1, 1)))
    raised = False
    try:
        user.email = "b@petasight.com"  # type: ignore[misc]
    except Exception:
        raised = True
    assert raised


def test_conversation_from_row():
    created = datetime(2026, 1, 2, 9, 30, 0)
    convo = Conversation.from_row((5, 7, "Trip planning", created))
    assert convo.id == 5
    assert convo.user_id == 7
    assert convo.title == "Trip planning"
    assert convo.created_at == created


def test_message_from_row():
    created = datetime(2026, 1, 3, 8, 0, 0)
    msg = Message.from_row((9, 5, 7, "assistant", "hi there", "#dc1414", "temperature", created))
    assert msg.id == 9
    assert msg.conversation_id == 5
    assert msg.user_id == 7
    assert msg.role == "assistant"
    assert msg.content == "hi there"
    assert msg.bubble_color == "#dc1414"
    assert msg.color_rule == "temperature"
    assert msg.created_at == created


def _run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    _run()
