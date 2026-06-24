"""Stateless session tokens — an HMAC-signed, self-contained credential.

Token format:  <b64url(payload_json)>.<b64url(hmac_sha256(payload_json))>

The payload carries the server-established identity (`sub` = user_id), plus `iat`/`exp`
(lifetime) and a random `jti` (uniqueness + future revocation handle). Verification recomputes
the HMAC with SESSION_SECRET and constant-time compares, then checks expiry — so there is no
server-side session store (fits serverless). Pure/stdlib, and the secret is injectable for tests.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

COOKIE_NAME = "session"
SESSION_TTL_SECONDS = 8 * 60 * 60  # short-lived; bounds the replay window (see THREATS T1)
_SECRET_ENV = "SESSION_SECRET"


class SessionError(Exception):
    """Raised when the server is misconfigured (e.g. SESSION_SECRET missing)."""


def _secret() -> bytes:
    value = os.environ.get(_SECRET_ENV)
    if not value:
        raise SessionError(f"{_SECRET_ENV} is not set")
    return value.encode("utf-8")


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64d(text: str) -> bytes:
    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + padding)


def _sign(payload: dict, secret: bytes) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    sig = hmac.new(secret, raw, hashlib.sha256).digest()
    return f"{_b64e(raw)}.{_b64e(sig)}"


def issue(user_id: int, email: str, *, ttl: int = SESSION_TTL_SECONDS, secret: bytes | None = None) -> str:
    """Mint a signed session token for an authenticated user."""
    now = int(time.time())
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": now + ttl,
        "jti": secrets.token_urlsafe(8),
    }
    return _sign(payload, secret or _secret())


def verify(token: str, *, secret: bytes | None = None) -> dict | None:
    """Return the payload if the token is authentic and unexpired, else None."""
    key = secret or _secret()
    try:
        raw_b64, sig_b64 = token.split(".")
        raw = _b64d(raw_b64)
        sig = _b64d(sig_b64)
    except (ValueError, TypeError):
        return None

    expected = hmac.new(key, raw, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, expected):
        return None

    try:
        payload = json.loads(raw)
    except (ValueError, TypeError):
        return None

    if int(payload.get("exp", 0)) < int(time.time()):
        return None
    return payload


def build_session_cookie(token: str, *, ttl: int = SESSION_TTL_SECONDS) -> str:
    """Set-Cookie value carrying the session: HttpOnly, Secure, SameSite=Lax."""
    return (
        f"{COOKIE_NAME}={token}; Max-Age={ttl}; Path=/; "
        "HttpOnly; Secure; SameSite=Lax"
    )


def clear_session_cookie() -> str:
    """Set-Cookie value that deletes the session cookie (logout)."""
    return f"{COOKIE_NAME}=; Max-Age=0; Path=/; HttpOnly; Secure; SameSite=Lax"


def read_token_from_cookies(cookie_header: str | None) -> str | None:
    """Extract the session token from a request Cookie header, if present."""
    if not cookie_header:
        return None
    for part in cookie_header.split(";"):
        name, _, value = part.strip().partition("=")
        if name == COOKIE_NAME:
            return value or None
    return None
