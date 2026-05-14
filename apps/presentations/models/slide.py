from django.db import models

from apps.core.constants import SlideLayout
from apps.core.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Slide(UUIDPrimaryKeyMixin, TimestampMixin):
    presentation = models.ForeignKey(
        "presentations.Presentation",
        on_delete=models.CASCADE,
        related_name="slides",
    )
    heading = models.CharField(max_length=500, blank=True, default="")
    body = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    layout = models.CharField(
        max_length=50,
        choices=[(layout.value, layout.name) for layout in SlideLayout],
        default=SlideLayout.CONTENT,
    )
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "slides"
        ordering = ["position"]
        indexes = [
            models.Index(fields=["presentation", "position"]),
        ]

    def __str__(self) -> str:
        return f"Slide {self.position}: {self.heading}"
