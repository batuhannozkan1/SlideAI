from __future__ import annotations

from typing import Sequence

from apps.core.base_repository import BaseRepository
from apps.presentations.models import SlideTemplate


class TemplateRepository(BaseRepository[SlideTemplate]):
    model = SlideTemplate

    def list_active(self, **kwargs) -> Sequence[SlideTemplate]:
        return list(
            SlideTemplate.objects.filter(is_active=True, **kwargs).order_by("name")
        )
