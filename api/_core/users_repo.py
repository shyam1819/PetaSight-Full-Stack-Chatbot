"""User data access — the only place that knows SQL for the users table.

The auth service depends on the UserRepository interface (not on psycopg), so it can be
unit-tested with an in-memory fake.
"""
from __future__ import annotations

from typing import Protocol

from api._core.db import connect
from api._core.models import USER_COLUMNS, User


class UserRepository(Protocol):
    def find_by_email(self, email: str) -> User | None: ...
    def get_by_id(self, user_id: int) -> User | None: ...
    def create(self, email: str, password_hash: str) -> User: ...


class PostgresUserRepository:
    """UserRepository backed by Neon Postgres."""

    def find_by_email(self, email: str) -> User | None:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(f"select {USER_COLUMNS} from users where email = %s", (email,))
            row = cur.fetchone()
        return User.from_row(row) if row else None

    def get_by_id(self, user_id: int) -> User | None:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(f"select {USER_COLUMNS} from users where id = %s", (user_id,))
            row = cur.fetchone()
        return User.from_row(row) if row else None

    def create(self, email: str, password_hash: str) -> User:
        """Insert a new user. Raises on duplicate email (UNIQUE constraint)."""
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                f"insert into users (email, password_hash) values (%s, %s) "
                f"returning {USER_COLUMNS}",
                (email, password_hash),
            )
            row = cur.fetchone()
            conn.commit()
        return User.from_row(row)
