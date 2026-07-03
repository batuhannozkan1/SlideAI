"""URL map for the mobile REST API, mounted at /api/v1/ by config/urls.py."""
from __future__ import annotations

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ai_views,
    auth_views,
    export_views,
    presentation_views,
    slide_views,
    theme_views,
)

app_name = "api"

urlpatterns = [
    # Auth
    path("auth/register/", auth_views.RegisterView.as_view(), name="register"),
    path("auth/login/", auth_views.LoginView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/me/", auth_views.CurrentUserView.as_view(), name="me"),
    # Presentations
    path(
        "presentations/",
        presentation_views.PresentationListCreateView.as_view(),
        name="presentation-list",
    ),
    path(
        "presentations/<uuid:pk>/",
        presentation_views.PresentationDetailView.as_view(),
        name="presentation-detail",
    ),
    path(
        "presentations/<uuid:pk>/duplicate/",
        presentation_views.PresentationDuplicateView.as_view(),
        name="presentation-duplicate",
    ),
    # Slides (nested under a presentation for list/create/reorder)
    path(
        "presentations/<uuid:pk>/slides/",
        slide_views.SlideListCreateView.as_view(),
        name="slide-list",
    ),
    path(
        "presentations/<uuid:pk>/slides/reorder/",
        slide_views.SlideReorderView.as_view(),
        name="slide-reorder",
    ),
    path("slides/<uuid:pk>/", slide_views.SlideDetailView.as_view(), name="slide-detail"),
    # Themes / templates / dashboard
    path("themes/", theme_views.ThemeListView.as_view(), name="theme-list"),
    path("templates/", theme_views.TemplateListView.as_view(), name="template-list"),
    path("dashboard/stats/", theme_views.DashboardStatsView.as_view(), name="dashboard-stats"),
    # AI
    path("ai/generate/", ai_views.GenerateView.as_view(), name="ai-generate"),
    path("ai/slides/<uuid:pk>/edit/", ai_views.SlideEditView.as_view(), name="ai-slide-edit"),
    # Export
    path(
        "presentations/<uuid:pk>/export/pptx/",
        export_views.ExportPptxView.as_view(),
        name="export-pptx",
    ),
]
