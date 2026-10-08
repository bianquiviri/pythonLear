"""Client CRUD endpoints."""

from __future__ import annotations

import math
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.adapters.inbound.web.deps import (
    get_client_service,
    get_current_user,
    require_admin,
    translate_domain_error,
)
from app.adapters.inbound.web.schemas import (
    ClientCreate,
    ClientList,
    ClientRead,
    ClientUpdate,
    PageMeta,
)
from app.application.client_services import ClientService, CreateClientCommand, UpdateClientCommand
from app.domain.errors import DomainError
from app.domain.user import User

router = APIRouter(prefix="/api/v1/clients", tags=["clients"])


@router.get("", response_model=ClientList, summary="List clients with pagination and search")
async def list_clients(
    service: Annotated[ClientService, Depends(get_client_service)],
    _: Annotated[User, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(max_length=100)] = None,
) -> ClientList:
    items, total = await service.list(page=page, per_page=per_page, search=search)
    return ClientList(
        items=[ClientRead.model_validate(item) for item in items],
        meta=PageMeta(
            page=page,
            per_page=per_page,
            total=total,
            pages=math.ceil(total / per_page) if total else 0,
        ),
    )


@router.get("/{client_id}", response_model=ClientRead, summary="Get a client by id")
async def get_client(
    client_id: int,
    service: Annotated[ClientService, Depends(get_client_service)],
    _: Annotated[User, Depends(get_current_user)],
) -> ClientRead:
    try:
        client = await service.get(client_id)
    except DomainError as exc:
        raise translate_domain_error(exc) from exc
    return ClientRead.model_validate(client)


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate,
    service: Annotated[ClientService, Depends(get_client_service)],
    _: Annotated[User, Depends(get_current_user)],
) -> ClientRead:
    try:
        client = await service.create(
            CreateClientCommand(
                name=payload.name,
                email=payload.email,
                phone=payload.phone,
                address=payload.address,
                notes=payload.notes,
            )
        )
    except DomainError as exc:
        raise translate_domain_error(exc) from exc
    return ClientRead.model_validate(client)


@router.put("/{client_id}", response_model=ClientRead, summary="Update a client")
async def update_client(
    client_id: int,
    payload: ClientUpdate,
    service: Annotated[ClientService, Depends(get_client_service)],
    _: Annotated[User, Depends(get_current_user)],
) -> ClientRead:
    try:
        client = await service.update(client_id, UpdateClientCommand(**payload.model_dump()))
    except DomainError as exc:
        raise translate_domain_error(exc) from exc
    return ClientRead.model_validate(client)


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a client (admin only)",
)
async def delete_client(
    client_id: int,
    service: Annotated[ClientService, Depends(get_client_service)],
    _: Annotated[User, Depends(require_admin)],
) -> None:
    try:
        await service.delete(client_id)
    except DomainError as exc:
        raise translate_domain_error(exc) from exc
