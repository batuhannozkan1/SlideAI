from __future__ import annotations

import uuid

import pytest

from apps.presentations.models import Presentation
from apps.presentations.tests.factories import create_test_presentation, create_test_slide

pytestmark = pytest.mark.django_db

LIST = "/api/v1/presentations/"


def detail(pk) -> str:
    return f"/api/v1/presentations/{pk}/"


def test_list_is_empty_for_new_user(auth_client):
    resp = auth_client.get(LIST)
    assert resp.status_code == 200
    body = resp.json()
    assert body["results"] == []
    assert body["pagination"]["total_count"] == 0


def test_create_presentation(auth_client, theme):
    resp = auth_client.post(
        LIST,
        {"title": "Quarterly Review", "description": "Q3", "theme_id": str(theme.id)},
        format="json",
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Quarterly Review"
    assert body["theme"]["id"] == str(theme.id)
    assert Presentation.objects.filter(id=body["id"]).exists()


def test_list_only_returns_owner_presentations(auth_client, user, other_user):
    create_test_presentation(user, title="Mine")
    create_test_presentation(other_user, title="Theirs")
    body = auth_client.get(LIST).json()
    titles = [p["title"] for p in body["results"]]
    assert "Mine" in titles
    assert "Theirs" not in titles
    assert body["pagination"]["total_count"] == 1


def test_detail_includes_ordered_slides(auth_client, presentation):
    create_test_slide(presentation, heading="B", position=1)
    create_test_slide(presentation, heading="A", position=0)
    body = auth_client.get(detail(presentation.id)).json()
    assert [s["heading"] for s in body["slides"]] == ["A", "B"]


def test_cross_owner_detail_forbidden(other_auth_client, presentation):
    resp = other_auth_client.get(detail(presentation.id))
    assert resp.status_code == 403
    assert resp["content-type"].startswith("application/json")


def test_missing_presentation_returns_json_404(auth_client):
    resp = auth_client.get(detail(uuid.uuid4()))
    assert resp.status_code == 404
    assert "detail" in resp.json()


def test_patch_updates_fields(auth_client, presentation):
    resp = auth_client.patch(
        detail(presentation.id), {"title": "Renamed", "is_public": True}, format="json"
    )
    assert resp.status_code == 200
    presentation.refresh_from_db()
    assert presentation.title == "Renamed"
    assert presentation.is_public is True


def test_soft_delete_then_absent_from_list(auth_client, presentation):
    assert auth_client.delete(detail(presentation.id)).status_code == 204
    presentation.refresh_from_db()
    assert presentation.is_deleted is True
    assert auth_client.get(LIST).json()["pagination"]["total_count"] == 0


def test_duplicate_copies_presentation_with_slides(auth_client, presentation):
    create_test_slide(presentation, heading="Slide 1", position=0)
    resp = auth_client.post(f"/api/v1/presentations/{presentation.id}/duplicate/")
    assert resp.status_code == 201
    body = resp.json()
    assert "(Kopya)" in body["title"]
    assert body["id"] != str(presentation.id)
    assert body["slide_count"] == 1
