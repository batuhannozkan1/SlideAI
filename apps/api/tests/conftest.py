from __future__ import annotations

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.presentations.models import Theme
from apps.presentations.tests.factories import (
    create_test_presentation,
    create_test_slide,
    create_test_user,
)

PASSWORD = "StrongPass123"


def _bearer(client: APIClient, user) -> APIClient:
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return client


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db):
    return create_test_user(username="alice", email="alice@example.com", password=PASSWORD)


@pytest.fixture
def other_user(db):
    return create_test_user(username="bob", email="bob@example.com", password=PASSWORD)


@pytest.fixture
def auth_client(db, user) -> APIClient:
    return _bearer(APIClient(), user)


@pytest.fixture
def other_auth_client(db, other_user) -> APIClient:
    return _bearer(APIClient(), other_user)


@pytest.fixture
def theme(db) -> Theme:
    return Theme.objects.create(
        name="Corporate Blue",
        primary_color="#0066cc",
        secondary_color="#0b1120",
        accent_color="#00aaff",
        font_heading="Inter",
        font_body="Inter",
    )


@pytest.fixture
def presentation(db, user):
    return create_test_presentation(user, title="My Deck")


@pytest.fixture
def slide(db, presentation):
    return create_test_slide(presentation, heading="Intro", position=0)
