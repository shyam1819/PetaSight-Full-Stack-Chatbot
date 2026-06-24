"""Unit tests for the chat service (stories 3.6 + 5.3) — fakes, no DB/network."""
from datetime import datetime

from api._core.bubble_rules import decimal_color, temperature_color
from api._core.chat_service import ChatService
from api._core.llm import MessageAnalysis
from api._core.models import Message


class FakeLLM:
    def __init__(self, analysis: MessageAnalysis):
        self._analysis = analysis
        self.last_history = None

    def analyze(self, message, history=None) -> MessageAnalysis:
        self.last_history = history
        return self._analysis


class FakeConversationRepo:
    """owned: set of (conversation_id, user_id) pairs that exist for that user."""

    def __init__(self, owned=()):
        self._owned = set(owned)

    def get(self, conversation_id, user_id):
        return object() if (conversation_id, user_id) in self._owned else None


class FakeMessageRepo:
    def __init__(self):
        self.added: list[Message] = []
        self._next = 100

    def add(self, conversation_id, user_id, role, content, bubble_color=None, color_rule=None):
        self._next += 1
        msg = Message(
            self._next, conversation_id, user_id, role, content, bubble_color, color_rule, datetime.now()
        )
        self.added.append(msg)
        return msg

    def list_for_conversation(self, conversation_id, user_id):
        return [m for m in self.added if m.conversation_id == conversation_id and m.user_id == user_id]


def _svc(analysis, *, owned=()):
    return ChatService(FakeLLM(analysis), FakeConversationRepo(owned), FakeMessageRepo())


def _analysis(**kw):
    base = dict(reply="ok", city=None, temperature_c=None, decimal_value=None, panic="calm")
    base.update(kw)
    return MessageAnalysis(**base)


# --- build_reply (compute) ---

def test_build_reply_temperature():
    a = _analysis(reply="Stay cool", city="Austin", temperature_c=21.5, panic="neutral")
    out = _svc(a).build_reply("Austin 21.5C")
    assert out.reply == "Stay cool"
    assert out.rule == "temperature"
    assert out.bubble_color == temperature_color(21.5).to_hex()


def test_build_reply_decimal_uses_message_regex():
    out = _svc(_analysis(reply="Noted")).build_reply("the total came to 42.37")
    assert out.rule == "decimal"
    assert out.bubble_color == decimal_color(37).to_hex()


# --- send_message (orchestration + persistence) ---

def test_send_message_persists_user_and_assistant():
    a = _analysis(reply="Warm!", city="Austin", temperature_c=21.5, panic="neutral")
    svc = _svc(a, owned={(1, 7)})
    turn = svc.send_message(conversation_id=1, user_id=7, text="Austin 21.5C")
    assert turn is not None
    assert turn.user_message.role == "user" and turn.user_message.content == "Austin 21.5C"
    assert turn.user_message.bubble_color is None  # user bubble has no colour
    assert turn.assistant_message.role == "assistant"
    assert turn.assistant_message.content == "Warm!"


def test_send_message_assistant_has_colour_and_rule():
    a = _analysis(reply="Warm!", city="Austin", temperature_c=21.5, panic="neutral")
    svc = _svc(a, owned={(1, 7)})
    turn = svc.send_message(1, 7, "Austin 21.5C")
    assert turn.assistant_message.bubble_color == temperature_color(21.5).to_hex()
    assert turn.assistant_message.color_rule == "temperature"


def test_send_message_rejects_unowned_conversation():
    svc = _svc(_analysis(), owned=set())  # conversation (1,7) not owned
    assert svc.send_message(1, 7, "hello") is None


def test_send_message_passes_prior_history_to_llm():
    llm = FakeLLM(_analysis(reply="ok"))
    convos = FakeConversationRepo({(1, 7)})
    msgs = FakeMessageRepo()
    msgs.add(1, 7, "user", "earlier question")
    msgs.add(1, 7, "assistant", "earlier answer", "#fff", "panic")
    ChatService(llm, convos, msgs).send_message(1, 7, "new question")
    assert llm.last_history == [("user", "earlier question"), ("assistant", "earlier answer")]
    # the current message must NOT be in the history passed to the LLM
    assert ("user", "new question") not in (llm.last_history or [])


def _run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    _run()
