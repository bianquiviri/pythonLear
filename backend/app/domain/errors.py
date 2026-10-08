"""Domain errors — raised by the domain/application layers, never by adapters."""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all business-rule errors."""


class ValidationError(DomainError):
    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(message)
        self.field = field


class NotFoundError(DomainError):
    def __init__(self, entity: str, identifier: object) -> None:
        super().__init__(f"{entity} not found: {identifier}")
        self.entity = entity
        self.identifier = identifier


class ConflictError(DomainError):
    pass


class AuthenticationError(DomainError):
    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(message)


class AuthorizationError(DomainError):
    def __init__(self, message: str = "Not enough permissions") -> None:
        super().__init__(message)
