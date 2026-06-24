"""Integration check for PostgresUserRepository against live Neon (story 2.3).

Not a unit test — needs a real DB connection. Loads .env.neon, exercises create/find/get/
duplicate, and cleans up the test row. Run manually:
    PYTHONPATH=. <venv>/bin/python tests/integration_users_repo.py
"""
import os
import re
import secrets

# Load the pulled env (pooled connection) into the process.
env = {}
with open(".env.neon") as f:
    for line in f:
        m = re.match(r'^([A-Za-z0-9_]+)="?(.*?)"?$', line.strip())
        if m:
            env[m.group(1)] = m.group(2)
os.environ.setdefault("petasight_postgres_DATABASE_URL", env["petasight_postgres_DATABASE_URL"])

from api._core.db import connect  # noqa: E402
from api._core.users_repo import PostgresUserRepository  # noqa: E402

repo = PostgresUserRepository()
email = f"itest+{secrets.token_hex(4)}@petasight.com"

try:
    created = repo.create(email, "pbkdf2_sha256$1$salt$hash")
    assert created.id and created.email == email, "create returns the new user"

    found = repo.find_by_email(email)
    assert found and found.id == created.id, "find_by_email finds it"

    by_id = repo.get_by_id(created.id)
    assert by_id and by_id.email == email, "get_by_id finds it"

    assert repo.find_by_email("does-not-exist@petasight.com") is None, "missing email -> None"

    duplicate_raised = False
    try:
        repo.create(email, "x")
    except Exception:
        duplicate_raised = True
    assert duplicate_raised, "duplicate email raises"

    print(f"integration OK — user id={created.id} email={email}")
finally:
    with connect() as conn, conn.cursor() as cur:
        cur.execute("delete from users where email = %s", (email,))
        conn.commit()
    print("cleaned up test user")
