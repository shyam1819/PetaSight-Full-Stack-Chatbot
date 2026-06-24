"""Password hashing — PBKDF2-HMAC-SHA256 with a per-password salt.

Pure and dependency-free (stdlib only), so it unit-tests without DB or network.
Stored format (self-describing, so iterations/salt travel with the hash):

    pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

_ALGORITHM = "pbkdf2_sha256"
_ITERATIONS = 210_000
_SALT_BYTES = 16
_HASH_BYTES = 32


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii")


def _b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text.encode("ascii"))


def hash_password(password: str, *, iterations: int = _ITERATIONS) -> str:
    """Hash a password into the self-describing stored format."""
    if not password:
        raise ValueError("password must not be empty")
    salt = secrets.token_bytes(_SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations, _HASH_BYTES
    )
    return f"{_ALGORITHM}${iterations}${_b64e(salt)}${_b64e(derived)}"


def verify_password(password: str, stored: str) -> bool:
    """Constant-time check of a password against a stored hash.

    Returns False (never raises) for malformed/unknown stored values.
    """
    try:
        algorithm, iter_str, salt_b64, hash_b64 = stored.split("$")
        if algorithm != _ALGORITHM:
            return False
        iterations = int(iter_str)
        salt = _b64d(salt_b64)
        expected = _b64d(hash_b64)
    except (ValueError, TypeError):
        return False
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations, len(expected)
    )
    return hmac.compare_digest(derived, expected)
