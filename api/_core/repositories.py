"""Repository interfaces (abstractions).

Deliberately free of any DB/driver imports, so the service layer can depend on these
abstractions (Dependency Inversion) without pulling in psycopg — which keeps services
unit-testable with in-memory fakes.
"""
from __future__ import annotations

from typing import Protocol

from api._core.models import User


class UserRepository(Protocol):
    def find_by_email(self, email: str) -> User | None: ...
    def get_by_id(self, user_id: int) -> User | None: ...
    def create(self, email: str, password_hash: str) -> User: ...
