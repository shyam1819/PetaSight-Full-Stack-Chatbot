"""Unit tests for the auth service (story 2.4) — fake repo, injected secret, no DB."""
from datetime import datetime

from api._core import sessions
from api._core.auth_service import AuthOutcome, AuthService
from api._core.models import User
from api._core.passwords import verify_password

SECRET = b"test-secret-not-for-production"


class FakeUserRepo:
    def __init__(self):
        self._by_email: dict[str, User] = {}
        self._by_id: dict[int, User] = {}
        self._next_id = 1

    def find_by_email(self, email):
        return self._by_email.get(email)

    def get_by_id(self, user_id):
        return self._by_id.get(user_id)

    def create(self, email, password_hash):
        if email in self._by_email:
            raise ValueError("duplicate email")
        user = User(self._next_id, email, password_hash, datetime.now())
        self._by_email[email] = user
        self._by_id[user.id] = user
        self._next_id += 1
        return user


def _svc(repo=None):
    return AuthService(repo or FakeUserRepo(), session_secret=SECRET)


def test_first_login_creates_user():
    repo = FakeUserRepo()
    res = _svc(repo).login_or_register("alice@petasight.com", "pw1")
    assert res.outcome is AuthOutcome.CREATED and res.ok
    assert res.user is not None and res.token is not None
    stored = repo.find_by_email("alice@petasight.com")
    assert verify_password("pw1", stored.password_hash)
    payload = sessions.verify(res.token, secret=SECRET)
    assert payload is not None and payload["sub"] == res.user.id


def test_returning_login_authenticates():
    repo = FakeUserRepo()
    svc = _svc(repo)
    svc.login_or_register("alice@petasight.com", "pw1")
    res = svc.login_or_register("alice@petasight.com", "pw1")
    assert res.outcome is AuthOutcome.AUTHENTICATED and res.ok and res.token


def test_wrong_password_rejected_without_overwrite():
    repo = FakeUserRepo()
    svc = _svc(repo)
    svc.login_or_register("alice@petasight.com", "right-password")
    original_hash = repo.find_by_email("alice@petasight.com").password_hash
    res = svc.login_or_register("alice@petasight.com", "wrong-password")
    assert res.outcome is AuthOutcome.INVALID_CREDENTIALS
    assert not res.ok and res.token is None
    assert repo.find_by_email("alice@petasight.com").password_hash == original_hash


def test_non_petasight_domain_blocked():
    res = _svc().login_or_register("eve@gmail.com", "pw")
    assert res.outcome is AuthOutcome.DOMAIN_NOT_ALLOWED and not res.ok


def test_missing_fields():
    assert _svc().login_or_register("", "pw").outcome is AuthOutcome.MISSING_FIELDS
    assert _svc().login_or_register("a@petasight.com", "").outcome is AuthOutcome.MISSING_FIELDS


def test_email_normalized_to_one_account():
    repo = FakeUserRepo()
    svc = _svc(repo)
    svc.login_or_register("  Alice@Petasight.COM ", "pw1")
    res = svc.login_or_register("alice@petasight.com", "pw1")
    assert res.outcome is AuthOutcome.AUTHENTICATED
    assert len(repo._by_email) == 1


def _run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    _run()
