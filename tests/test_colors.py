"""Unit tests for the colour primitives (story 3.1) — pure, no deps."""
from api._core.colors import Color, clamp, lerp, lerp_color, ramp


def test_color_to_hex():
    assert Color(0, 0, 139).to_hex() == "#00008b"
    assert Color(255, 255, 255).to_hex() == "#ffffff"
    assert Color(220, 20, 20).to_hex() == "#dc1414"


def test_clamp():
    assert clamp(40, 0, 35) == 35
    assert clamp(-5, 0, 35) == 0
    assert clamp(12, 0, 35) == 12


def test_lerp():
    assert lerp(0, 10, 0.0) == 0
    assert lerp(0, 10, 1.0) == 10
    assert lerp(0, 10, 0.5) == 5


def test_lerp_color_midpoint_and_clamping():
    black, white = Color(0, 0, 0), Color(255, 255, 255)
    assert lerp_color(black, white, 0.5) == Color(128, 128, 128)
    # f is clamped, so out-of-range maps to the endpoints
    assert lerp_color(black, white, 2.0) == white
    assert lerp_color(black, white, -1.0) == black


def test_ramp_three_stops():
    black, gray, white = Color(0, 0, 0), Color(128, 128, 128), Color(255, 255, 255)
    stops = [(0.0, white), (0.5, gray), (1.0, black)]
    assert ramp(stops, 0.0) == white
    assert ramp(stops, 1.0) == black
    assert ramp(stops, 0.5) == gray
    # below/above range clamps to the ends
    assert ramp(stops, -2.0) == white
    assert ramp(stops, 9.0) == black
    # quarter point lands between white and gray
    quarter = ramp(stops, 0.25)
    assert quarter == lerp_color(white, gray, 0.5)


def _run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    _run()
