"""Unit tests: AuthService with fakes for ports."""

from __future__ import annotations

import pytest

from app.application.auth_service import AuthService, LoginCommand, RegisterCommand
from app.domain.errors import AuthenticationError, ValidationError
from app.domain.user import ROLE_ADMIN, ROLE_VIEWER, User


class FakeHasher:
    def hash(self, plain: str) -> str:
        return f"hashed::{plain}"

    def verify(self, plain: str, hashed: str) -> bool:
        return hashed == f"hashed::{plain}"


class FakeTokens:
    def encode(self, subject: str, role: str) -> str:
        return f"token::{subject}::{role}"

    def decode(self, token: str) -> dict:
        try:
            _, sub, role = token.split("::")
        except ValueError as exc:
            raise AuthenticationError("Invalid token") from exc
        return {"sub": sub, "role": role}


class FakeUsers:
    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._next_id = 1

    async def add(self, user: User) -> User:
        user.id = self._next_id
        self._next_id += 1
        self._users[user.id] = user
        return user

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._users.values() if u.email == email.lower()), None)

    async def get(self, user_id: int) -> User | None:
        return self._users.get(user_id)


@pytest.fixture
def auth_service() -> AuthService:
    return AuthService(FakeUsers(), FakeHasher(), FakeTokens())


async def test_login_success_returns_token(auth_service: AuthService):
    await auth_service.register(
        RegisterCommand(email="a@b.co", password="password1", full_name="A")
    )
    token = await auth_service.login(LoginCommand(email="a@b.co", password="password1"))
    assert token.startswith("token::")


async def test_login_wrong_password_rejected(auth_service: AuthService):
    await auth_service.register(
        RegisterCommand(email="a@b.co", password="password1", full_name="A")
    )
    with pytest.raises(AuthenticationError):
        await auth_service.login(LoginCommand(email="a@b.co", password="wrong"))


async def test_login_unknown_user_rejected(auth_service: AuthService):
    with pytest.raises(AuthenticationError):
        await auth_service.login(LoginCommand(email="ghost@b.co", password="whatever"))


async def test_register_short_password_rejected(auth_service: AuthService):
    with pytest.raises(ValidationError):
        await auth_service.register(
            RegisterCommand(email="a@b.co", password="short", full_name="A")
        )


async def test_register_duplicate_email_rejected(auth_service: AuthService):
    await auth_service.register(
        RegisterCommand(email="a@b.co", password="password1", full_name="A")
    )
    with pytest.raises(ValidationError):
        await auth_service.register(
            RegisterCommand(email="a@b.co", password="password1", full_name="B")
        )


async def test_current_user_from_token(auth_service: AuthService):
    user = await auth_service.register(
        RegisterCommand(email="a@b.co", password="password1", full_name="A", role=ROLE_ADMIN)
    )
    token = await auth_service.login(LoginCommand(email="a@b.co", password="password1"))
    current = await auth_service.current_user(token)
    assert current.id == user.id
    assert current.role == ROLE_ADMIN
    assert current.is_admin


async def test_current_user_invalid_token(auth_service: AuthService):
    with pytest.raises(AuthenticationError):
        await auth_service.current_user("garbage")


def test_viewer_is_not_admin():
    user = User(email="v@b.co", password_hash="x", role=ROLE_VIEWER)
    assert not user.is_admin
