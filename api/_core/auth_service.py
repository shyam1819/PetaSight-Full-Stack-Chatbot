"""Authentication logic — pure decisions over a UserRepository.

Depends only on the repository interface plus the password/session primitives, so it unit-tests
with an in-memory fake repo and an injected session secret (no DB, no env).

Policy (Feature 4 + DECISIONS):
  - only @petasight.com emails are allowed (enforced here, server-side);
  - trust-on-first-use: an unknown email creates the account with the given password;
  - a known email with a wrong password is rejected and never overwritten (no takeover).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from api._core.models import User
from api._core.passwords import hash_password, verify_password
from api._core.repositories import UserRepository
from api._core.sessions import issue

ALLOWED_DOMAIN = "@petasight.com"


class AuthOutcome(str, Enum):
    CREATED = "created"
    AUTHENTICATED = "authenticated"
    INVALID_CREDENTIALS = "invalid_credentials"
    DOMAIN_NOT_ALLOWED = "domain_not_allowed"
    MISSING_FIELDS = "missing_fields"


@dataclass(frozen=True)
class AuthResult:
    outcome: AuthOutcome
    user: User | None = None
    token: str | None = None

    @property
    def ok(self) -> bool:
        return self.outcome in (AuthOutcome.CREATED, AuthOutcome.AUTHENTICATED)


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        *,
        allowed_domain: str = ALLOWED_DOMAIN,
        session_secret: bytes | None = None,
    ):
        self._users = users
        self._allowed_domain = allowed_domain
        self._session_secret = session_secret

    def login_or_register(self, email: str, password: str) -> AuthResult:
        email = (email or "").strip().lower()
        if not email or not password:
            return AuthResult(AuthOutcome.MISSING_FIELDS)
        if not email.endswith(self._allowed_domain):
            return AuthResult(AuthOutcome.DOMAIN_NOT_ALLOWED)

        existing = self._users.find_by_email(email)
        if existing is None:
            # Trust-on-first-use: unknown email becomes a new account.
            # (A rare concurrent first-login could collide on the UNIQUE email; acceptable here.)
            user = self._users.create(email, hash_password(password))
            return AuthResult(AuthOutcome.CREATED, user=user, token=self._issue(user))

        if not verify_password(password, existing.password_hash):
            # Known email, wrong password — reject, never overwrite (prevents account takeover).
            return AuthResult(AuthOutcome.INVALID_CREDENTIALS)

        return AuthResult(AuthOutcome.AUTHENTICATED, user=existing, token=self._issue(existing))

    def _issue(self, user: User) -> str:
        return issue(user.id, user.email, secret=self._session_secret)
