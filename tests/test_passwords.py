"""Tests for the PBKDF2 password hashing module (story 2.1)."""
from api._core.passwords import hash_password, verify_password


def test_hash_verify_roundtrip():
    h = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", h)


def test_wrong_password_fails():
    h = hash_password("s3cret-value")
    assert not verify_password("wrong", h)


def test_salt_is_unique_per_hash():
    assert hash_password("same") != hash_password("same")


def test_stored_format():
    parts = hash_password("x").split("$")
    assert parts[0] == "pbkdf2_sha256"
    assert len(parts) == 4
    assert int(parts[1]) > 0


def test_malformed_stored_returns_false():
    assert not verify_password("x", "not-a-valid-hash")
    assert not verify_password("x", "")


def test_empty_password_raises():
    raised = False
    try:
        hash_password("")
    except ValueError:
        raised = True
    assert raised


def _run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    _run()
