from django.conf import settings
from django.db import models

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Presentation(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="presentations",
    )
    theme = models.ForeignKey(
        "presentations.Theme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="presentations",
    )
    is_public = models.BooleanField(default=False)
    slide_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "presentations"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["owner", "-updated_at"]),
        ]

    def __str__(self) -> str:
        return self.title
