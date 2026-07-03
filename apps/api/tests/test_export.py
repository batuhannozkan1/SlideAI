from __future__ import annotations

import pytest

from apps.presentations.tests.factories import create_test_slide

pytestmark = pytest.mark.django_db

PPTX_CT = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


def export_url(pres_id) -> str:
    return f"/api/v1/presentations/{pres_id}/export/pptx/"


def test_export_pptx_returns_binary_attachment(auth_client, presentation):
    create_test_slide(presentation, heading="Slide", position=0)
    resp = auth_client.get(export_url(presentation.id))
    assert resp.status_code == 200
    assert resp["content-type"] == PPTX_CT
    assert "attachment" in resp["content-disposition"]
    assert len(resp.content) > 0


def test_export_cross_owner_forbidden(other_auth_client, presentation):
    assert other_auth_client.get(export_url(presentation.id)).status_code == 403
