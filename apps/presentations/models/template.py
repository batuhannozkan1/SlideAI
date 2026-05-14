from django.db import models

from apps.core.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class SlideTemplate(UUIDPrimaryKeyMixin, TimestampMixin):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, default="")
    thumbnail_url = models.URLField(blank=True, default="")
    structure = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "slide_templates"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
