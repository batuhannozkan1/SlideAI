"""Auth endpoints: register, login (JWT obtain), current user.

Token refresh is handled directly by simplejwt's ``TokenRefreshView`` in urls.
Login reuses the project's ``EmailAuthBackend`` (email + password) via Django's
``authenticate`` — so API and SSR login share identical semantics.
"""
from __future__ import annotations

from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.services.auth_service import register_user
from apps.accounts.services.profile_service import get_profile

from ..serializers import LoginSerializer, MeSerializer, RegisterSerializer, UserSerializer


def _tokens_for(user) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # register_user raises ConflictError (→409) on a duplicate email.
        result = register_user(
            username=serializer.validated_data["username"],
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        user = result.data
        return Response(
            {"user": UserSerializer(user).data, **_tokens_for(user)},
            status=201,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            raise AuthenticationFailed("Geçersiz e-posta veya şifre.")
        return Response(_tokens_for(user))


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = get_profile(user.id).data
        payload = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
        }
        return Response(MeSerializer(payload).data)
