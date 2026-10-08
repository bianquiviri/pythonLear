"""UserRepository adapter over SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import select

from app.adapters.out.db.models import UserRow
from app.domain.user import User


def _to_domain(row: UserRow) -> User:
    return User(
        id=row.id,
        email=row.email,
        password_hash=row.password_hash,
        full_name=row.full_name,
        role=row.role,
        is_active=row.is_active,
        created_at=row.created_at,
    )


class SqlUserRepository:
    def __init__(self, session) -> None:
        self._session = session

    async def add(self, user: User) -> User:
        row = UserRow(
            email=user.email,
            password_hash=user.password_hash,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return _to_domain(row)

    async def get_by_email(self, email: str) -> User | None:
        row = await self._session.scalar(select(UserRow).where(UserRow.email == email.lower()))
        return _to_domain(row) if row else None

    async def get(self, user_id: int) -> User | None:
        row = await self._session.get(UserRow, user_id)
        return _to_domain(row) if row else None
