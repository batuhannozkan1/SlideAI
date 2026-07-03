from django.contrib import admin
from django.urls import include, path

from apps.core.views import landing_view
from apps.presentations.views import presentation_views, template_views

urlpatterns = [
    path("", landing_view, name="landing"),
    path("dashboard/", presentation_views.dashboard, name="dashboard"),
    path("templates/", template_views.template_gallery, name="template-gallery"),
    path("templates/<uuid:pk>/preview/", template_views.template_preview, name="template-preview"),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("presentations/", include("apps.presentations.urls", namespace="presentations")),
    # REST API for the mobile client (additive; SSR routes above are untouched).
    path("api/v1/", include("apps.api.urls")),
]
