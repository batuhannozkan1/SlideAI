from __future__ import annotations

from rest_framework import serializers


class ThemeSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    primary_color = serializers.CharField(read_only=True)
    secondary_color = serializers.CharField(read_only=True)
    accent_color = serializers.CharField(read_only=True)
    font_heading = serializers.CharField(read_only=True)
    font_body = serializers.CharField(read_only=True)


class TemplateSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_blank=True)
    thumbnail_url = serializers.CharField(read_only=True, allow_blank=True)
    structure = serializers.JSONField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
