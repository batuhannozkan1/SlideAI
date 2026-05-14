from __future__ import annotations

from typing import Sequence
from uuid import UUID

from django.db.models import Prefetch

from apps.core.base_repository import BaseRepository
from apps.presentations.models import Presentation, Slide


class PresentationRepository(BaseRepository[Presentation]):
    model = Presentation

    def get_with_slides(self, pk: UUID) -> Presentation | None:
        try:
            return (
                Presentation.objects.prefetch_related(
                    Prefetch("slides", queryset=Slide.objects.order_by("position"))
                ).get(pk=pk, is_deleted=False)
            )
        except Presentation.DoesNotExist:
            return None

    def list_by_owner(
        self, owner_id: int, *, limit: int = 50, offset: int = 0
    ) -> Sequence[Presentation]:
        return list(
            Presentation.objects.filter(owner_id=owner_id, is_deleted=False).order_by(
                "-updated_at"
            )[offset : offset + limit]
        )

    def list_public(
        self, *, limit: int = 50, offset: int = 0
    ) -> Sequence[Presentation]:
        return list(
            Presentation.objects.filter(is_public=True, is_deleted=False).order_by(
                "-updated_at"
            )[offset : offset + limit]
        )
