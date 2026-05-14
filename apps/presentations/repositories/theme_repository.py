from __future__ import annotations

from typing import Sequence

from apps.core.base_repository import BaseRepository
from apps.presentations.models import Theme


class ThemeRepository(BaseRepository[Theme]):
    model = Theme

    def list_active(self, **kwargs) -> Sequence[Theme]:
        return list(Theme.objects.filter(is_active=True, **kwargs).order_by("name"))
