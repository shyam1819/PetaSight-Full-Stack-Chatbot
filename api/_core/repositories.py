"""Repository interfaces (abstractions).

Deliberately free of any DB/driver imports, so the service layer can depend on these
abstractions (Dependency Inversion) without pulling in psycopg — which keeps services
unit-testable with in-memory fakes.
"""
from __future__ import annotations

from typing import Protocol

from api._core.models import Conversation, User


class UserRepository(Protocol):
    def find_by_email(self, email: str) -> User | None: ...
    def get_by_id(self, user_id: int) -> User | None: ...
    def create(self, email: str, password_hash: str) -> User: ...


class ConversationRepository(Protocol):
    # Every method is scoped by user_id so per-user isolation is the default (EP-5/THREATS).
    def create(self, user_id: int, title: str | None = None) -> Conversation: ...
    def list_by_user(self, user_id: int) -> list[Conversation]: ...
    def get(self, conversation_id: int, user_id: int) -> Conversation | None: ...
