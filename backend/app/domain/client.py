"""Client entity — pure domain, no framework imports."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.errors import ValidationError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass
class Client:
    id: int | None = None
    name: str = ""
    email: str = ""
    phone: str | None = None
    address: str | None = None
    notes: str | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValidationError("name is required", "name")
        if len(self.name) > 120:
            raise ValidationError("name must be at most 120 characters", "name")
        if not self.email or not EMAIL_RE.match(self.email):
            raise ValidationError("email is not valid", "email")
        self.email = self.email.strip().lower()
        if self.phone and len(self.phone) > 30:
            raise ValidationError("phone must be at most 30 characters", "phone")

    def update(
        self,
        *,
        name: str | None = None,
        phone: str | None = None,
        address: str | None = None,
        notes: str | None = None,
        is_active: bool | None = None,
    ) -> Client:
        if name is not None:
            self.name = name
        if phone is not None:
            self.phone = phone
        if address is not None:
            self.address = address
        if notes is not None:
            self.notes = notes
        if is_active is not None:
            self.is_active = is_active
        self.updated_at = _now()
        self.validate()
        return self
