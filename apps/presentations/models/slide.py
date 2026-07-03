from django.db import models

from apps.core.constants import SlideType
from apps.core.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Slide(UUIDPrimaryKeyMixin, TimestampMixin):
    presentation = models.ForeignKey(
        "presentations.Presentation",
        on_delete=models.CASCADE,
        related_name="slides",
    )
    heading = models.CharField(max_length=500, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    slide_type = models.CharField(
        max_length=20,
        choices=[(t.value, t.name) for t in SlideType],
        default=SlideType.SPLIT,
    )
    # Structured content payload. Shape depends on slide_type
    # (see apps/ai/prompts/slide_generation.py for the schema).
    content = models.JSONField(default=dict, blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "slides"
        ordering = ["position"]
        indexes = [
            models.Index(fields=["presentation", "position"]),
        ]

    def __str__(self) -> str:
        return f"Slide {self.position}: {self.heading}"
