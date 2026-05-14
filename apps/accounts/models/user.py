from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.mixins import TimestampMixin


class User(TimestampMixin, AbstractUser):
    email = models.EmailField(unique=True)

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return self.email
