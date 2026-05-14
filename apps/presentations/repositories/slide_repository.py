from __future__ import annotations

from typing import Sequence
from uuid import UUID

from apps.core.base_repository import BaseRepository
from apps.presentations.models import Slide


class SlideRepository(BaseRepository[Slide]):
    model = Slide

    def list_by_presentation(self, presentation_id: UUID) -> Sequence[Slide]:
        return list(
            Slide.objects.filter(presentation_id=presentation_id).order_by("position")
        )

    def get_max_position(self, presentation_id: UUID) -> int:
        last = (
            Slide.objects.filter(presentation_id=presentation_id)
            .order_by("-position")
            .first()
        )
        return last.position if last else -1

    def reorder(self, slide_ids: Sequence[UUID]) -> None:
        for position, slide_id in enumerate(slide_ids):
            Slide.objects.filter(pk=slide_id).update(position=position)
