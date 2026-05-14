from django.urls import path

from apps.accounts.views import auth_views, profile_views

app_name = "accounts"

urlpatterns = [
    path("register/", auth_views.register_view, name="register"),
    path("login/", auth_views.login_view, name="login"),
    path("logout/", auth_views.logout_view, name="logout"),
    path("profile/", profile_views.profile_view, name="profile"),
    path("profile/edit/", profile_views.profile_edit_view, name="profile-edit"),
]
