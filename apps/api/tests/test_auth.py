from __future__ import annotations

import pytest

from apps.accounts.models import User
from .conftest import PASSWORD

pytestmark = pytest.mark.django_db

REGISTER = "/api/v1/auth/register/"
LOGIN = "/api/v1/auth/login/"
REFRESH = "/api/v1/auth/token/refresh/"
ME = "/api/v1/auth/me/"


def test_register_creates_user_and_returns_tokens(api_client):
    resp = api_client.post(
        REGISTER,
        {"username": "carol", "email": "carol@example.com", "password": PASSWORD},
        format="json",
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["access"] and body["refresh"]
    assert body["user"]["email"] == "carol@example.com"
    assert User.objects.filter(email="carol@example.com").exists()
    # A profile is created alongside the user.
    assert User.objects.get(email="carol@example.com").profile is not None


def test_register_duplicate_email_conflicts(api_client, user):
    resp = api_client.post(
        REGISTER,
        {"username": "dupe", "email": user.email, "password": PASSWORD},
        format="json",
    )
    assert resp.status_code == 409
    assert "detail" in resp.json()


def test_register_weak_password_rejected(api_client):
    resp = api_client.post(
        REGISTER,
        {"username": "weak", "email": "weak@example.com", "password": "123"},
        format="json",
    )
    assert resp.status_code == 400


def test_login_returns_tokens(api_client, user):
    resp = api_client.post(
        LOGIN, {"email": user.email, "password": PASSWORD}, format="json"
    )
    assert resp.status_code == 200
    assert resp.json()["access"] and resp.json()["refresh"]


def test_login_wrong_password_unauthorized(api_client, user):
    resp = api_client.post(
        LOGIN, {"email": user.email, "password": "wrong-pass-000"}, format="json"
    )
    assert resp.status_code == 401


def test_token_refresh_issues_new_access(api_client, user):
    login = api_client.post(
        LOGIN, {"email": user.email, "password": PASSWORD}, format="json"
    ).json()
    resp = api_client.post(REFRESH, {"refresh": login["refresh"]}, format="json")
    assert resp.status_code == 200
    assert resp.json()["access"]


def test_me_requires_authentication(api_client):
    assert api_client.get(ME).status_code == 401


def test_me_returns_profile(auth_client, user):
    resp = auth_client.get(ME)
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == user.email
    assert "bio" in body and "avatar_url" in body
