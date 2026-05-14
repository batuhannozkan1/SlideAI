from django.db import models

from apps.core.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Theme(UUIDPrimaryKeyMixin, TimestampMixin):
    name = models.CharField(max_length=255, unique=True)
    primary_color = models.CharField(max_length=7, default="#000000")
    secondary_color = models.CharField(max_length=7, default="#ffffff")
    accent_color = models.CharField(max_length=7, default="#0066cc")
    font_heading = models.CharField(max_length=100, default="Arial")
    font_body = models.CharField(max_length=100, default="Arial")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "themes"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
