"""Authentication use cases."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.errors import AuthenticationError, ValidationError
from app.domain.user import User
from app.ports import PasswordHasher, TokenProvider, UserRepository

MIN_PASSWORD_LEN = 8


@dataclass(frozen=True)
class LoginCommand:
    email: str
    password: str


@dataclass(frozen=True)
class RegisterCommand:
    email: str
    password: str
    full_name: str
    role: str = "viewer"


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        tokens: TokenProvider,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    async def login(self, cmd: LoginCommand) -> str:
        user = await self._users.get_by_email(cmd.email)
        if user is None or not user.is_active:
            raise AuthenticationError()
        if not self._hasher.verify(cmd.password, user.password_hash):
            raise AuthenticationError()
        return self._tokens.encode(str(user.id), user.role)

    async def current_user(self, token: str) -> User:
        payload = self._tokens.decode(token)
        subject = payload.get("sub")
        if subject is None:
            raise AuthenticationError("Invalid token")
        try:
            user_id = int(str(subject))
        except (TypeError, ValueError):
            raise AuthenticationError("Invalid token") from None
        user = await self._users.get(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("User no longer active")
        return user

    async def register(self, cmd: RegisterCommand) -> User:
        if len(cmd.password) < MIN_PASSWORD_LEN:
            raise ValidationError(
                f"password must be at least {MIN_PASSWORD_LEN} characters", "password"
            )
        existing = await self._users.get_by_email(cmd.email)
        if existing is not None:
            raise ValidationError("email already registered", "email")
        user = User(
            email=cmd.email,
            password_hash=self._hasher.hash(cmd.password),
            full_name=cmd.full_name,
            role=cmd.role,
        )
        return await self._users.add(user)
