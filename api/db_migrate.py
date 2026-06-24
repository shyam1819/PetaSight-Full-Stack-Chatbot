"""TEMPORARY migrate endpoint — applies the idempotent schema to the app's OWN database
(whatever Neon branch the deployment is bound to), then reports the result. Removed after.
"""
from http.server import BaseHTTPRequestHandler

from api._core.db import _dsn, connect
from api._core.http_helpers import send_json

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS conversations (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    bubble_color TEXT,
    color_rule TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE messages ADD COLUMN IF NOT EXISTS color_rule TEXT;
CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id);
"""


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            dsn = _dsn()
            host = dsn.split("@")[1].split("/")[0] if "@" in dsn else "?"
            dbname = dsn.split("/")[-1].split("?")[0]
            with connect() as conn, conn.cursor() as cur:
                cur.execute(_SCHEMA)
                conn.commit()
                cur.execute(
                    "select column_name from information_schema.columns "
                    "where table_name='messages' order by ordinal_position"
                )
                cols = [r[0] for r in cur.fetchall()]
                cur.execute("select count(*) from conversations")
                ccount = cur.fetchone()[0]
            send_json(
                self,
                200,
                {
                    "host": host,
                    "dbname": dbname,
                    "messages_columns": cols,
                    "conversations_count": ccount,
                },
            )
        except Exception as exc:  # noqa: BLE001
            send_json(self, 500, {"error": type(exc).__name__, "detail": str(exc)[:300]})
