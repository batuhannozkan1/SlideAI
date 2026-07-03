from __future__ import annotations

import pytest

from apps.presentations.tests.factories import create_test_slide

pytestmark = pytest.mark.django_db


def slides_url(pres_id) -> str:
    return f"/api/v1/presentations/{pres_id}/slides/"


def slide_url(slide_id) -> str:
    return f"/api/v1/slides/{slide_id}/"


COVER = {"eyebrow": "Sunum", "subtitle": "Genel bakış", "icon": "fa-rocket", "date": "2026"}
SPLIT = {
    "eyebrow": "Bölüm 1",
    "points": [{"kind": "ok", "label": "Artı", "text": "İyi"}],
    "visual": {"type": "donut", "data": {"percent": 70, "center": "%70", "label": "Oran"}},
}
CLOSING = {"subtitle": "Teşekkürler", "stats": [{"value": "100%", "label": "Kapsam"}]}


def test_list_slides(auth_client, presentation):
    create_test_slide(presentation, heading="One", position=0)
    body = auth_client.get(slides_url(presentation.id)).json()
    assert len(body["results"]) == 1
    assert body["results"][0]["heading"] == "One"


def test_create_slide_bumps_count(auth_client, presentation):
    resp = auth_client.post(
        slides_url(presentation.id),
        {"heading": "New", "slide_type": "split", "content": SPLIT},
        format="json",
    )
    assert resp.status_code == 201
    presentation.refresh_from_db()
    assert presentation.slide_count == 1


@pytest.mark.parametrize(
    "slide_type,content",
    [("cover", COVER), ("split", SPLIT), ("closing", CLOSING)],
)
def test_content_json_roundtrips_per_type(auth_client, presentation, slide_type, content):
    resp = auth_client.post(
        slides_url(presentation.id),
        {"heading": "H", "slide_type": slide_type, "content": content},
        format="json",
    )
    assert resp.status_code == 201
    sid = resp.json()["id"]
    fetched = auth_client.get(slide_url(sid)).json()
    assert fetched["slide_type"] == slide_type
    assert fetched["content"] == content


def test_update_slide(auth_client, slide):
    resp = auth_client.patch(
        slide_url(slide.id), {"heading": "Updated"}, format="json"
    )
    assert resp.status_code == 200
    slide.refresh_from_db()
    assert slide.heading == "Updated"


def test_delete_slide_decrements_count(auth_client, presentation):
    s = create_test_slide(presentation, heading="x", position=0)
    presentation.slide_count = 1
    presentation.save(update_fields=["slide_count"])
    assert auth_client.delete(slide_url(s.id)).status_code == 204
    presentation.refresh_from_db()
    assert presentation.slide_count == 0


def test_reorder_slides(auth_client, presentation):
    a = create_test_slide(presentation, heading="A", position=0)
    b = create_test_slide(presentation, heading="B", position=1)
    resp = auth_client.post(
        f"/api/v1/presentations/{presentation.id}/slides/reorder/",
        {"slide_ids": [str(b.id), str(a.id)]},
        format="json",
    )
    assert resp.status_code == 200
    body = auth_client.get(slides_url(presentation.id)).json()
    assert [s["heading"] for s in body["results"]] == ["B", "A"]


def test_cross_owner_slide_create_forbidden(other_auth_client, presentation):
    resp = other_auth_client.post(
        slides_url(presentation.id),
        {"heading": "x", "slide_type": "split", "content": SPLIT},
        format="json",
    )
    assert resp.status_code == 403
