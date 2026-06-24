"""DB connectivity check — confirms the deployed function can reach Neon.

Self-contained (no shared imports) so it verifies only the DB wiring. Returns a
generic reason on failure; it never echoes the connection string or secrets.
"""
from http.server import BaseHTTPRequestHandler
import os
import json

# The Neon/Vercel integration prefixes vars; fall back to plain names too.
DSN_CANDIDATES = (
    "DATABASE_URL",
    "petasight_postgres_DATABASE_URL",
    "POSTGRES_URL",
    "petasight_postgres_POSTGRES_URL",
)


def _dsn():
    for name in DSN_CANDIDATES:
        value = os.environ.get(name)
        if value:
            return value, name
    return None, None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        dsn, source = _dsn()
        if not dsn:
            return self._send(500, {"db": "error", "reason": "no_connection_string"})
        try:
            import psycopg

            with psycopg.connect(dsn, connect_timeout=10) as conn:
                with conn.cursor() as cur:
                    cur.execute("select 1")
                    cur.fetchone()
                    cur.execute(
                        "select count(*) from information_schema.tables "
                        "where table_schema = 'public' "
                        "and table_name in ('users', 'conversations', 'messages')"
                    )
                    tables = cur.fetchone()[0]
            return self._send(200, {"db": "ok", "via": source, "expected_tables": tables})
        except Exception as exc:
            return self._send(500, {"db": "error", "reason": type(exc).__name__})

    def _send(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)
