"""Postgres connection helper shared by the repositories.

Reads the pooled Neon connection string (the Vercel/Neon integration prefixes it). The pooled
endpoint (PgBouncer) suits many short-lived serverless connections. Repositories open a
connection per call and use it as a context manager, so it's committed and closed deterministically.
"""
from __future__ import annotations

import os

import psycopg

_DSN_CANDIDATES = (
    "DATABASE_URL",
    "petasight_postgres_DATABASE_URL",
    "POSTGRES_URL",
    "petasight_postgres_POSTGRES_URL",
)


class DatabaseError(Exception):
    """Raised when no connection string is configured."""


def _dsn() -> str:
    for name in _DSN_CANDIDATES:
        value = os.environ.get(name)
        if value:
            return value
    raise DatabaseError("No Postgres connection string found in environment")


def connect() -> psycopg.Connection:
    """Open a new connection. Use as a context manager (commits/closes on exit)."""
    return psycopg.connect(_dsn(), connect_timeout=10)
