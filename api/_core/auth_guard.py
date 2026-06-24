"""Authentication guard — the single place that turns a request's session cookie into a
server-established identity. Every protected endpoint calls `require_user()` first.

`authenticate()` is the pure decision (unit-testable with an injected secret); `require_user()`
is the thin handler glue that emits 401/503 on failure.
"""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from api._core.http_helpers import send_json
from api._core.sessions import SessionError, read_token_from_cookies, verify


def authenticate(cookie_header: str | None, *, secret: bytes | None = None) -> dict | None:
    """Return the verified session payload (identity) for a Cookie header, else None.

    Raises SessionError only if the server is misconfigured (SESSION_SECRET missing).
    """
    token = read_token_from_cookies(cookie_header)
    if not token:
        return None
    return verify(token, secret=secret)


def require_user(handler: BaseHTTPRequestHandler) -> dict | None:
    """Guard for protected handlers.

    Returns the identity payload (`payload['sub']` is the server-established user_id), or sends a
    401 (not authenticated) / 503 (misconfigured) response and returns None — so the handler can
    simply `if user is None: return`. Identity is taken from the verified signature, never from
    client-supplied input.
    """
    try:
        payload = authenticate(handler.headers.get("Cookie"))
    except SessionError:
        send_json(handler, 503, {"message": "Server not configured."})
        return None
    if not payload:
        send_json(handler, 401, {"message": "Not authenticated."})
        return None
    return payload
