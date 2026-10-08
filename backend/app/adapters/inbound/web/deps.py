"""FastAPI dependencies — the composition root wiring ports to adapters."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.out.auth.jwt_token import JwtTokenProvider
from app.adapters.out.auth.pwd import BcryptPasswordHasher
from app.adapters.out.db.client_repository import SqlClientRepository
from app.adapters.out.db.session import get_session
from app.adapters.out.db.user_repository import SqlUserRepository
from app.application.auth_service import AuthService
from app.application.client_services import ClientService
from app.domain.errors import AuthenticationError, AuthorizationError
from app.domain.user import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db(request: Request) -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session


def get_client_service(session: Annotated[AsyncSession, Depends(get_db)]) -> ClientService:
    return ClientService(SqlClientRepository(session))


def get_auth_service(session: Annotated[AsyncSession, Depends(get_db)]) -> AuthService:
    return AuthService(SqlUserRepository(session), BcryptPasswordHasher(), JwtTokenProvider())


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return await auth.current_user(credentials.credentials)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return user


def translate_domain_error(exc: Exception) -> HTTPException:
    from app.domain.errors import (
        AuthenticationError,
        ConflictError,
        NotFoundError,
        ValidationError,
    )

    if isinstance(exc, NotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ConflictError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, ValidationError):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    if isinstance(exc, AuthenticationError):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    if isinstance(exc, AuthorizationError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    raise exc
