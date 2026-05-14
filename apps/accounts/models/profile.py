from django.conf import settings
from django.db import models

from apps.core.mixins import TimestampMixin


class UserProfile(TimestampMixin, models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.TextField(blank=True, default="")
    avatar_url = models.URLField(blank=True, default="")

    class Meta:
        db_table = "user_profiles"

    def __str__(self) -> str:
        return f"Profile of {self.user}"
