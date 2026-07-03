from __future__ import annotations

from django.conf import settings
from rest_framework import serializers

_STYLES = ("professional", "creative", "academic", "casual")
_LANGUAGES = ("tr", "en")


class AIGenerateSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=500)
    num_slides = serializers.IntegerField(min_value=1)
    style = serializers.ChoiceField(choices=_STYLES, default="professional")
    language = serializers.ChoiceField(choices=_LANGUAGES, default="tr")
    additional_instructions = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    template_id = serializers.UUIDField(required=False, allow_null=True)
    theme_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_num_slides(self, value: int) -> int:
        max_slides = getattr(settings, "AI_MAX_SLIDES", 20)
        if value > max_slides:
            raise serializers.ValidationError(
                f"En fazla {max_slides} slayt üretilebilir."
            )
        return value


class AISlideEditSerializer(serializers.Serializer):
    instruction = serializers.CharField(max_length=2000)
    change_topic = serializers.BooleanField(default=False)
    # Prior chat turns as [{"role": "user"|"assistant", "text": "..."}].
    history = serializers.ListField(
        child=serializers.DictField(), required=False, default=list
    )
