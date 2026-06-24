"""Unit tests for the bubble colour rules (story 3.2+)."""
from api._core.bubble_rules import (
    BRIGHT_RED,
    DEEP_BLUE,
    LIGHT_PURPLE,
    temperature_color,
    temperature_rule,
)
from api._core.colors import lerp_color
from api._core.llm import MessageAnalysis


def _analysis(*, city=None, temperature_c=None, decimal_value=None, panic="calm"):
    return MessageAnalysis(
        reply="r", city=city, temperature_c=temperature_c, decimal_value=decimal_value, panic=panic
    )


def test_temperature_color_anchors():
    assert temperature_color(0) == DEEP_BLUE
    assert temperature_color(15) == LIGHT_PURPLE
    assert temperature_color(35) == BRIGHT_RED


def test_temperature_color_clamped():
    assert temperature_color(-5) == DEEP_BLUE
    assert temperature_color(40) == BRIGHT_RED


def test_temperature_color_interpolates():
    # 7.5°C is halfway between 0 (blue) and 15 (purple)
    assert temperature_color(7.5) == lerp_color(DEEP_BLUE, LIGHT_PURPLE, 0.5)
    # 25°C is halfway between 15 (purple) and 35 (red)
    assert temperature_color(25) == lerp_color(LIGHT_PURPLE, BRIGHT_RED, 0.5)


def test_temperature_rule_requires_city_and_temp():
    assert temperature_rule("Austin 21.5", _analysis(city="Austin", temperature_c=21.5)) is not None
    assert temperature_rule("21.5 only", _analysis(temperature_c=21.5)) is None  # no city
    assert temperature_rule("Austin", _analysis(city="Austin")) is None  # no temp


def _run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    _run()
