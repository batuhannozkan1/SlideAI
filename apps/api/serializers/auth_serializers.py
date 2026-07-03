"""Auth serializers — output mappers for the user + plain input validators.

No ``.save()`` and no ``ModelSerializer``: persistence stays in the service
layer (``auth_service`` / ``profile_service``). These only validate input and
shape output.
"""
from __future__ import annotations

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class UserSerializer(serializers.Serializer):
    """Public shape of a User (read-only output)."""

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True, allow_blank=True)
    last_name = serializers.CharField(read_only=True, allow_blank=True)


class MeSerializer(serializers.Serializer):
    """User + profile, fed a plain dict by the /auth/me/ view."""

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True, allow_blank=True)
    last_name = serializers.CharField(read_only=True, allow_blank=True)
    bio = serializers.CharField(read_only=True, allow_blank=True)
    avatar_url = serializers.CharField(read_only=True, allow_blank=True)
