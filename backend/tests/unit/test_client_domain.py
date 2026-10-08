"""Unit tests: Client domain entity rules."""

from __future__ import annotations

import pytest

from app.domain.client import Client
from app.domain.errors import ValidationError


def test_valid_client_is_created():
    client = Client(name="Ada", email="Ada@Example.COM")
    assert client.email == "ada@example.com"
    assert client.is_active is True
    assert client.id is None


@pytest.mark.parametrize("email", ["", "not-an-email", "a@b", "@nope.com"])
def test_invalid_email_rejected(email: str):
    with pytest.raises(ValidationError) as exc:
        Client(name="Ada", email=email)
    assert exc.value.field == "email"


def test_empty_name_rejected():
    with pytest.raises(ValidationError) as exc:
        Client(name="   ", email="a@b.co")
    assert exc.value.field == "name"


def test_long_name_rejected():
    with pytest.raises(ValidationError):
        Client(name="x" * 121, email="a@b.co")


def test_update_changes_fields_and_sets_timestamp():
    client = Client(name="Ada", email="ada@example.com")
    assert client.updated_at is None
    client.update(phone="+1-555", address="Somewhere", is_active=False)
    assert client.phone == "+1-555"
    assert client.address == "Somewhere"
    assert client.is_active is False
    assert client.updated_at is not None


def test_update_with_invalid_values_fails():
    client = Client(name="Ada", email="ada@example.com")
    with pytest.raises(ValidationError):
        client.update(name="")
