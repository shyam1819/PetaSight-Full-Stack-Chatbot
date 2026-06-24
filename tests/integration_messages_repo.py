"""Integration check for PostgresMessageRepository against live Neon (story 5.2).

Applies the idempotent schema (so the color_rule column exists), then proves message-level
isolation: user B cannot read user A's messages even with the conversation_id. Cleans up.
    PYTHONPATH=. <venv>/bin/python tests/integration_messages_repo.py
"""
import os
import re
import secrets

env = {}
with open(".env.neon") as f:
    for line in f:
        m = re.match(r'^([A-Za-z0-9_]+)="?(.*?)"?$', line.strip())
        if m:
            env[m.group(1)] = m.group(2)
os.environ.setdefault("petasight_postgres_DATABASE_URL", env["petasight_postgres_DATABASE_URL"])

from api._core.conversations_repo import PostgresConversationRepository  # noqa: E402
from api._core.db import connect  # noqa: E402
from api._core.messages_repo import PostgresMessageRepository  # noqa: E402
from api._core.users_repo import PostgresUserRepository  # noqa: E402

# Apply schema (idempotent) so color_rule exists on the live messages table.
with open("db/schema.sql") as f:
    schema_sql = f.read()
with connect() as conn, conn.cursor() as cur:
    cur.execute(schema_sql)
    conn.commit()

users = PostgresUserRepository()
convos = PostgresConversationRepository()
messages = PostgresMessageRepository()

suffix = secrets.token_hex(4)
email_a = f"itest-a+{suffix}@petasight.com"
email_b = f"itest-b+{suffix}@petasight.com"

try:
    user_a = users.create(email_a, "pbkdf2_sha256$1$s$h")
    user_b = users.create(email_b, "pbkdf2_sha256$1$s$h")
    convo = convos.create(user_a.id, title="A's chat")

    messages.add(convo.id, user_a.id, "user", "Austin 21.5C")
    asst = messages.add(convo.id, user_a.id, "assistant", "Warm!", "#ce72a2", "temperature")
    assert asst.bubble_color == "#ce72a2" and asst.color_rule == "temperature"

    history = messages.list_for_conversation(convo.id, user_a.id)
    assert [m.role for m in history] == ["user", "assistant"], "ordered history for the owner"
    assert history[1].bubble_color == "#ce72a2", "colour persisted + read back"

    other = messages.list_for_conversation(convo.id, user_b.id)
    assert other == [], "ISOLATION: B reads no messages from A's conversation"

    print(f"integration OK — convo {convo.id}, {len(history)} msgs; B isolated")
finally:
    with connect() as conn, conn.cursor() as cur:
        cur.execute("delete from users where email in (%s, %s)", (email_a, email_b))
        conn.commit()
    print("cleaned up test users + conversation + messages")
