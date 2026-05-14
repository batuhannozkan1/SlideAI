from django.contrib import admin
from django.urls import include, path

from apps.core.views import landing_view

urlpatterns = [
    path("", landing_view, name="landing"),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("presentations/", include("apps.presentations.urls", namespace="presentations")),
]
