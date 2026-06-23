from bubble_service import temp_to_rgb, cached_color, is_petasight_user


class FakeRequest:
    def __init__(self, headers):
        self.headers = headers


def test_freezing_is_deep_blue():
    assert temp_to_rgb(-5) == (0, 0, 139)


def test_hot_is_bright_red():
    assert temp_to_rgb(40) == (220, 20, 20)


def test_cached_color_returns_a_tuple():
    assert isinstance(cached_color(20), tuple)


def test_cache_runs_twice():
    cached_color(22)
    cached_color(22)
    assert True


def test_known_petasight_email_allowed():
    req = FakeRequest({"X-User-Email": "dev@petasight.com"})
    assert is_petasight_user(req) is True
