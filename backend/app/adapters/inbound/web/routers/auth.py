"""Auth endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.adapters.inbound.web.deps import get_auth_service, get_current_user, translate_domain_error
from app.adapters.inbound.web.schemas import LoginRequest, TokenResponse, UserRead
from app.application.auth_service import LoginCommand
from app.domain.errors import DomainError
from app.domain.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, summary="Exchange credentials for a JWT")
async def login(
    payload: LoginRequest,
    request: Request,
    auth: Annotated[object, Depends(get_auth_service)],
) -> TokenResponse:
    del request
    try:
        token = await auth.login(LoginCommand(email=payload.email, password=payload.password))  # type: ignore[attr-defined]
    except DomainError as exc:
        raise translate_domain_error(exc) from exc
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserRead, summary="Current authenticated user")
async def me(user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    return UserRead(id=user.id or 0, email=user.email, full_name=user.full_name, role=user.role)
