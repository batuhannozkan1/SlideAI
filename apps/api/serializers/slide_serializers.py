from __future__ import annotations

from rest_framework import serializers

_SLIDE_TYPES = ("cover", "split", "closing")


class SlideSerializer(serializers.Serializer):
    """Output mapper for a Slide model instance.

    ``content`` is passed through verbatim as JSON — its shape is polymorphic by
    ``slide_type`` and the client renders it.
    """

    id = serializers.UUIDField(read_only=True)
    slide_type = serializers.CharField(read_only=True)
    heading = serializers.CharField(read_only=True, allow_blank=True)
    notes = serializers.CharField(read_only=True, allow_blank=True)
    content = serializers.JSONField(read_only=True)
    position = serializers.IntegerField(read_only=True)


class SlideCreateSerializer(serializers.Serializer):
    heading = serializers.CharField(max_length=500, allow_blank=True, default="")
    slide_type = serializers.ChoiceField(choices=_SLIDE_TYPES, default="split")
    content = serializers.JSONField(default=dict)
    notes = serializers.CharField(allow_blank=True, default="")
    # -1 (default) tells the service to append at the end.
    position = serializers.IntegerField(default=-1)


class SlideUpdateSerializer(serializers.Serializer):
    heading = serializers.CharField(max_length=500, required=False, allow_blank=True)
    slide_type = serializers.ChoiceField(choices=_SLIDE_TYPES, required=False)
    content = serializers.JSONField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class SlideReorderSerializer(serializers.Serializer):
    slide_ids = serializers.ListField(
        child=serializers.UUIDField(), allow_empty=False
    )
