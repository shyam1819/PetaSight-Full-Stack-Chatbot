"""Integration check for PostgresConversationRepository against live Neon (story 5.1).

Proves per-user isolation: user B cannot get user A's conversation. Loads .env.neon, creates two
test users + a conversation, exercises list/get, and cleans up. Run manually:
    PYTHONPATH=. <venv>/bin/python tests/integration_conversations_repo.py
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
from api._core.users_repo import PostgresUserRepository  # noqa: E402

users = PostgresUserRepository()
convos = PostgresConversationRepository()

suffix = secrets.token_hex(4)
email_a = f"itest-a+{suffix}@petasight.com"
email_b = f"itest-b+{suffix}@petasight.com"

try:
    user_a = users.create(email_a, "pbkdf2_sha256$1$s$h")
    user_b = users.create(email_b, "pbkdf2_sha256$1$s$h")

    convo = convos.create(user_a.id, title="A's trip")
    assert convo.id and convo.user_id == user_a.id

    a_list = convos.list_by_user(user_a.id)
    assert [c.id for c in a_list] == [convo.id], "A sees their conversation"
    assert convos.list_by_user(user_b.id) == [], "B sees none"

    assert convos.get(convo.id, user_a.id) is not None, "owner can get it"
    assert convos.get(convo.id, user_b.id) is None, "ISOLATION: non-owner gets None"

    print(f"integration OK — convo {convo.id}; B isolated from A")
finally:
    with connect() as conn, conn.cursor() as cur:
        # ON DELETE CASCADE removes the conversation with the user.
        cur.execute("delete from users where email in (%s, %s)", (email_a, email_b))
        conn.commit()
    print("cleaned up test users + conversations")
