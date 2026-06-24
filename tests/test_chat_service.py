"""Unit tests for the chat service (story 3.6) — fake LLM, no DB/network."""
from api._core.bubble_rules import decimal_color, temperature_color
from api._core.chat_service import ChatService
from api._core.llm import MessageAnalysis


class FakeLLM:
    def __init__(self, analysis: MessageAnalysis):
        self._analysis = analysis

    def analyze(self, message: str) -> MessageAnalysis:
        return self._analysis


def _svc(analysis):
    return ChatService(FakeLLM(analysis))


def test_build_reply_temperature():
    a = MessageAnalysis(
        reply="Stay cool", city="Austin", temperature_c=21.5, decimal_value=None, panic="neutral"
    )
    out = _svc(a).build_reply("Austin 21.5C")
    assert out.reply == "Stay cool"
    assert out.rule == "temperature"
    assert out.bubble_color == temperature_color(21.5).to_hex()
    assert out.analysis is a  # provenance carried through


def test_build_reply_decimal_uses_message_regex():
    # no city/temp; the decimal is found in the MESSAGE (code-authoritative)
    a = MessageAnalysis(
        reply="Noted", city=None, temperature_c=None, decimal_value=None, panic="calm"
    )
    out = _svc(a).build_reply("the total came to 42.37")
    assert out.rule == "decimal"
    assert out.bubble_color == decimal_color(37).to_hex()


def test_build_reply_panic_fallback():
    a = MessageAnalysis(
        reply="Breathe", city=None, temperature_c=None, decimal_value=None, panic="panicked"
    )
    out = _svc(a).build_reply("help help help")
    assert out.rule == "panic"


def _run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    _run()
