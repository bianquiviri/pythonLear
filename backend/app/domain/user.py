"""User entity — pure domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.client import EMAIL_RE
from app.domain.errors import ValidationError

ROLE_ADMIN = "admin"
ROLE_VIEWER = "viewer"
ROLES = (ROLE_ADMIN, ROLE_VIEWER)


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass
class User:
    id: int | None = None
    email: str = ""
    password_hash: str = ""
    full_name: str = ""
    role: str = ROLE_VIEWER
    is_active: bool = True
    created_at: datetime = field(default_factory=_now)

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not self.email or not EMAIL_RE.match(self.email):
            raise ValidationError("email is not valid", "email")
        self.email = self.email.strip().lower()
        if not self.password_hash:
            raise ValidationError("password_hash is required", "password_hash")
        if self.role not in ROLES:
            raise ValidationError(f"role must be one of {ROLES}", "role")

    @property
    def is_admin(self) -> bool:
        return self.role == ROLE_ADMIN
