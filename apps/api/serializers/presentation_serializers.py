from __future__ import annotations

from rest_framework import serializers

from .theme_serializers import ThemeSerializer


class PresentationSerializer(serializers.Serializer):
    """Output mapper for a Presentation model instance.

    ``theme`` is nested (or null). The detail view adds a ``slides`` key
    alongside this payload.
    """

    id = serializers.UUIDField(read_only=True)
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_blank=True)
    owner_id = serializers.IntegerField(read_only=True)
    theme = ThemeSerializer(read_only=True, allow_null=True)
    is_public = serializers.BooleanField(read_only=True)
    slide_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class PresentationCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, default="")
    theme_id = serializers.UUIDField(required=False, allow_null=True)


class PresentationUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    theme_id = serializers.UUIDField(required=False, allow_null=True)
    is_public = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("No fields to update.")
        return attrs
