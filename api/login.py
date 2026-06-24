"""POST /api/login — sign in or register (trust-on-first-use).

Thin handler: delegates the decision to AuthService, then maps the outcome to a status code and
sets the session cookie on success. (Replaces the Task-1 stub.)
"""
from http.server import BaseHTTPRequestHandler

from api._core.auth_service import AuthOutcome, AuthService
from api._core.http_helpers import read_json, send_json
from api._core.sessions import SessionError, build_session_cookie
from api._core.users_repo import PostgresUserRepository

_STATUS = {
    AuthOutcome.CREATED: 201,
    AuthOutcome.AUTHENTICATED: 200,
    AuthOutcome.INVALID_CREDENTIALS: 401,
    AuthOutcome.DOMAIN_NOT_ALLOWED: 403,
    AuthOutcome.MISSING_FIELDS: 400,
}

_MESSAGE = {
    AuthOutcome.INVALID_CREDENTIALS: "Invalid email or password.",
    AuthOutcome.DOMAIN_NOT_ALLOWED: "Only @petasight.com accounts are allowed.",
    AuthOutcome.MISSING_FIELDS: "Email and password are required.",
}


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = read_json(self)
        service = AuthService(PostgresUserRepository())
        try:
            result = service.login_or_register(data.get("email", ""), data.get("password", ""))
        except SessionError:
            return send_json(self, 503, {"message": "Server not configured."})

        if result.ok:
            cookie = build_session_cookie(result.token)
            return send_json(
                self,
                _STATUS[result.outcome],
                {"user": {"id": result.user.id, "email": result.user.email}},
                {"Set-Cookie": cookie},
            )
        return send_json(self, _STATUS[result.outcome], {"message": _MESSAGE[result.outcome]})
