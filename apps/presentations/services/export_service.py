from __future__ import annotations

from uuid import UUID

from apps.core.dtos import ServiceResult
from apps.core.exceptions import NotFoundError
from apps.presentations.repositories import presentation_repo


def export_presentation(presentation_id: UUID, *, format: str) -> ServiceResult:
    presentation = presentation_repo.get_with_slides(presentation_id)
    if presentation is None:
        raise NotFoundError("Presentation", presentation_id)

    # Export logic will be implemented when export libraries are integrated
    return ServiceResult.ok(data={"presentation": presentation, "format": format})
