"""Unit tests for the auth guard's pure decision (story 2.6) — injected secret, no DB/HTTP."""
from api._core import sessions
from api._core.auth_guard import authenticate

SECRET = b"test-secret-not-for-production"


def test_valid_cookie_returns_identity():
    token = sessions.issue(7, "alice@petasight.com", secret=SECRET)
    payload = authenticate(f"session={token}; theme=dark", secret=SECRET)
    assert payload is not None
    assert payload["sub"] == 7
    assert payload["email"] == "alice@petasight.com"


def test_no_cookie_returns_none():
    assert authenticate(None, secret=SECRET) is None
    assert authenticate("theme=dark; other=1", secret=SECRET) is None


def test_tampered_cookie_returns_none():
    token = sessions.issue(7, "alice@petasight.com", secret=SECRET)
    bad = token[:-1] + ("A" if token[-1] != "A" else "B")
    assert authenticate(f"session={bad}", secret=SECRET) is None


def test_wrong_secret_returns_none():
    token = sessions.issue(7, "alice@petasight.com", secret=SECRET)
    assert authenticate(f"session={token}", secret=b"different-secret") is None


def test_expired_cookie_returns_none():
    token = sessions.issue(7, "alice@petasight.com", ttl=-1, secret=SECRET)
    assert authenticate(f"session={token}", secret=SECRET) is None


def _run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    _run()
