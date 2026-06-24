"""Unit tests for the LLM abstraction (story 4.1) — no network, no LangChain.

A FakeLLMClient stands in for the Groq client so the rest of the app can be tested offline.
"""
from api._core.llm import LLMClient, MessageAnalysis


class FakeLLMClient:
    def __init__(self, analysis: MessageAnalysis):
        self._analysis = analysis
        self.calls: list[str] = []

    def analyze(self, message: str) -> MessageAnalysis:
        self.calls.append(message)
        return self._analysis


def test_fake_satisfies_interface_and_returns_analysis():
    canned = MessageAnalysis(
        reply="Stay safe!", city="Austin", temperature_c=21.5, decimal_value=None, panic="panicked"
    )
    client: LLMClient = FakeLLMClient(canned)
    out = client.analyze("Austin 21.5 we need to leave now")
    assert out is canned
    assert out.city == "Austin" and out.temperature_c == 21.5 and out.panic == "panicked"


def test_message_analysis_holds_decimal_and_nulls():
    a = MessageAnalysis(
        reply="r", city=None, temperature_c=None, decimal_value="42.37", panic="calm"
    )
    assert a.decimal_value == "42.37"
    assert a.city is None and a.temperature_c is None and a.panic == "calm"


def _run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    _run()
