from __future__ import annotations

import pytest

from apps.presentations.models import SlideTemplate, Theme

pytestmark = pytest.mark.django_db


def test_themes_list_returns_active_only(auth_client, theme):
    Theme.objects.create(name="Hidden", is_active=False)
    body = auth_client.get("/api/v1/themes/").json()
    names = [t["name"] for t in body["results"]]
    assert "Corporate Blue" in names
    assert "Hidden" not in names


def test_templates_list_returns_active_only(auth_client):
    SlideTemplate.objects.create(name="Pitch", structure={"slides": []}, is_active=True)
    SlideTemplate.objects.create(name="Old", structure={}, is_active=False)
    body = auth_client.get("/api/v1/templates/").json()
    names = [t["name"] for t in body["results"]]
    assert "Pitch" in names
    assert "Old" not in names


def test_dashboard_stats_has_all_fields(auth_client):
    body = auth_client.get("/api/v1/dashboard/stats/").json()
    for field in (
        "total_presentations",
        "total_slides",
        "presentations_this_month",
        "growth_percentage",
        "draft_count",
        "published_count",
        "chart_labels",
        "chart_values",
        "chart_max",
    ):
        assert field in body


def test_protected_endpoint_requires_auth(api_client):
    assert api_client.get("/api/v1/presentations/").status_code == 401


def test_domain_errors_render_json_not_html(api_client, user):
    # Hitting a protected route without a token should yield JSON (DRF), never an
    # SSR HTML error page — proving the middleware /api/ guard works.
    resp = api_client.get("/api/v1/dashboard/stats/")
    assert resp.status_code == 401
    assert resp["content-type"].startswith("application/json")
