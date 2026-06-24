"""Tests for the stateless session token module (story 2.2).

A fixed secret is injected so the tests need no environment configuration.
"""
from api._core import sessions

SECRET = b"test-secret-not-for-production"


def test_issue_verify_roundtrip():
    token = sessions.issue(7, "alice@petasight.com", secret=SECRET)
    payload = sessions.verify(token, secret=SECRET)
    assert payload is not None
    assert payload["sub"] == 7
    assert payload["email"] == "alice@petasight.com"
    assert "jti" in payload


def test_tampered_payload_rejected():
    token = sessions.issue(7, "alice@petasight.com", secret=SECRET)
    raw_b64, sig_b64 = token.split(".")
    # Flip the last char of the payload segment.
    flipped = raw_b64[:-1] + ("A" if raw_b64[-1] != "A" else "B")
    assert sessions.verify(f"{flipped}.{sig_b64}", secret=SECRET) is None


def test_wrong_secret_rejected():
    token = sessions.issue(7, "alice@petasight.com", secret=SECRET)
    assert sessions.verify(token, secret=b"different-secret") is None


def test_expired_token_rejected():
    token = sessions.issue(7, "alice@petasight.com", ttl=-1, secret=SECRET)
    assert sessions.verify(token, secret=SECRET) is None


def test_malformed_token_rejected():
    assert sessions.verify("garbage", secret=SECRET) is None
    assert sessions.verify("a.b.c", secret=SECRET) is None


def test_jti_unique_per_issue():
    t1 = sessions.issue(7, "a@petasight.com", secret=SECRET)
    t2 = sessions.issue(7, "a@petasight.com", secret=SECRET)
    assert t1 != t2


def test_session_cookie_flags():
    cookie = sessions.build_session_cookie("tok")
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=Lax" in cookie
    assert cookie.startswith("session=tok")


def test_clear_cookie_expires():
    cookie = sessions.clear_session_cookie()
    assert "Max-Age=0" in cookie
    assert "HttpOnly" in cookie


def test_read_token_from_cookies():
    assert sessions.read_token_from_cookies("session=abc; other=1") == "abc"
    assert sessions.read_token_from_cookies("other=1") is None
    assert sessions.read_token_from_cookies(None) is None


def _run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    _run()
