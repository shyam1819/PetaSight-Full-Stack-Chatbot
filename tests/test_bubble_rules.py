"""Unit tests for the bubble colour rules (story 3.2+)."""
from api._core.bubble_rules import (
    BRIGHT_RED,
    DECIMAL_DARKEST,
    DECIMAL_LIGHTEST,
    DEEP_BLUE,
    LIGHT_PURPLE,
    PANIC_MAGENTA,
    PANIC_PALE_YELLOW,
    PANIC_VIOLET,
    decimal_color,
    decimal_rule,
    extract_standalone_decimal,
    panic_color,
    panic_rule,
    resolve_bubble_color,
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


def test_extract_standalone_decimal():
    assert extract_standalone_decimal("the total came to 42.37") == "42.37"
    assert extract_standalone_decimal("it's 21.5 degrees") == "21.5"
    assert extract_standalone_decimal("no decimals here") is None
    assert extract_standalone_decimal("meet at 3pm") is None  # integer, not a decimal
    assert extract_standalone_decimal("version 1.2.3") is None  # not standalone
    assert extract_standalone_decimal("ip 192.168.0.1") is None


def test_decimal_color_anchors():
    assert decimal_color(0) == DECIMAL_LIGHTEST
    assert decimal_color(99) == DECIMAL_DARKEST


def test_decimal_rule_first_two_fractional_digits():
    assert decimal_rule("total 42.37", _analysis()) == decimal_color(37)
    assert decimal_rule("about 0.5 units", _analysis()) == decimal_color(50)  # right-padded
    assert decimal_rule("pi is 3.14159", _analysis()) == decimal_color(14)
    assert decimal_rule("exactly 3.0", _analysis()) == DECIMAL_LIGHTEST  # .00 lightest


def test_decimal_rule_is_code_authoritative():
    # No decimal in the text → None, even though the LLM reported one. Regex (code) wins.
    assert decimal_rule("no numbers here", _analysis(decimal_value="99.99")) is None


def test_panic_color_categories():
    assert panic_color("calm") == PANIC_PALE_YELLOW
    assert panic_color("neutral") == PANIC_MAGENTA
    assert panic_color("panicked") == PANIC_VIOLET


def test_panic_rule_always_matches():
    assert panic_rule("anything", _analysis(panic="panicked")) == PANIC_VIOLET
    assert panic_rule("anything", _analysis(panic="neutral")) == PANIC_MAGENTA
    assert panic_rule("anything", _analysis(panic="calm")) == PANIC_PALE_YELLOW


def test_resolver_temperature_wins_when_temp_present():
    # With a unit the LLM populates temperature_c → rule 1 wins over decimal AND panic.
    out = resolve_bubble_color(
        "Austin 21.5°C we need to leave right now",
        _analysis(city="Austin", temperature_c=21.5, decimal_value="21.5", panic="panicked"),
    )
    assert out.rule == "temperature"
    assert out.color == temperature_color(21.5)


def test_resolver_bare_number_with_city_is_decimal():
    # No unit → temperature_c stays null → falls through to decimal (first-match over panic).
    out = resolve_bubble_color(
        "Austin 21.5 we need to leave right now",
        _analysis(city="Austin", temperature_c=None, decimal_value="21.5", panic="panicked"),
    )
    assert out.rule == "decimal"
    assert out.color == decimal_color(50)  # ".5" -> "50"


def test_resolver_falls_through_to_decimal():
    # no city → not temperature; standalone decimal → decimal wins.
    out = resolve_bubble_color("the total came to 42.37", _analysis(panic="neutral"))
    assert out.rule == "decimal"
    assert out.color == decimal_color(37)


def test_resolver_falls_through_to_panic():
    out = resolve_bubble_color("just checking in, all good", _analysis(panic="calm"))
    assert out.rule == "panic"
    assert out.color == PANIC_PALE_YELLOW


def _run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    _run()
