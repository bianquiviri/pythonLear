"""FastAPI application factory."""

from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable
from typing import cast

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.adapters.inbound.web.routers import auth, clients, health
from app.config import get_settings
from app.domain.errors import DomainError

settings = get_settings()
settings.ensure_secure()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("spa")

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])
state = {"limiter": limiter}


def create_app() -> FastAPI:
    app = FastAPI(
        title="Clients SPA API",
        description="Small SPA backend — client management with JWT auth (hexagonal).",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, cast(Callable, _rate_limit_exceeded_handler))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def log_requests(
        request: Request, call_next: Callable[[Request], Awaitable[JSONResponse]]
    ) -> JSONResponse:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s -> %s %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response

    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        from app.adapters.inbound.web.deps import translate_domain_error

        http_exc = translate_domain_error(exc)
        return JSONResponse(status_code=http_exc.status_code, content={"detail": http_exc.detail})

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(clients.router)
    return app


app = create_app()
