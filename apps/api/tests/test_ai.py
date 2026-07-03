from __future__ import annotations

import pytest

from apps.core.dtos import ServiceResult
from apps.presentations.models import Slide

pytestmark = pytest.mark.django_db

GENERATE = "/api/v1/ai/generate/"


def test_generate_creates_presentation_and_slides(auth_client):
    resp = auth_client.post(
        GENERATE,
        {"topic": "Yapay Zeka", "num_slides": 5, "language": "tr"},
        format="json",
    )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert len(body["slides"]) == 5
    assert body["slides"][0]["slide_type"] == "cover"
    assert body["slides"][-1]["slide_type"] == "closing"
    assert body["slide_count"] == 5


def test_generate_over_max_slides_rejected(auth_client, settings):
    settings.AI_MAX_SLIDES = 20
    resp = auth_client.post(
        GENERATE, {"topic": "X", "num_slides": 999}, format="json"
    )
    assert resp.status_code == 400


def test_generate_service_failure_returns_400(auth_client, monkeypatch):
    from apps.api.views import ai_views

    monkeypatch.setattr(
        ai_views,
        "generate_presentation_slides",
        lambda req: ServiceResult.fail({"generation": ["boş"]}),
    )
    resp = auth_client.post(
        GENERATE, {"topic": "X", "num_slides": 3}, format="json"
    )
    assert resp.status_code == 400
    assert resp.json()["errors"]["generation"] == ["boş"]


def test_slide_ai_edit_persists_and_returns_message(auth_client, presentation):
    slide = Slide.objects.create(
        presentation=presentation,
        heading="Orijinal",
        slide_type="split",
        content={"points": [{"kind": "ok", "label": "a", "text": "b"}]},
        position=0,
    )
    resp = auth_client.post(
        f"/api/v1/ai/slides/{slide.id}/edit/",
        {"instruction": "Daha kısa yaz"},
        format="json",
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert "message" in body
    # Topic lock: heading preserved when change_topic is false.
    assert body["slide"]["heading"] == "Orijinal"
