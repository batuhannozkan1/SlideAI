from __future__ import annotations

from uuid import UUID

from apps.core.dtos import ServiceResult
from apps.core.exceptions import NotFoundError, PermissionDeniedError
from apps.presentations.repositories import presentation_repo
from apps.presentations.services.exporters import get_exporter

# Auto-discover exporters
from apps.presentations.services.exporters import pptx_exporter as _  # noqa: F401


def export_presentation(
    presentation_id: UUID,
    format: str,
    *,
    user_id: int,
) -> ServiceResult:
    presentation = presentation_repo.get_with_slides(presentation_id)
    if presentation is None:
        raise NotFoundError("Presentation", presentation_id)

    if presentation.owner_id != user_id and not presentation.is_public:
        raise PermissionDeniedError("Bu sunuma erişim izniniz yok.")

    slides = list(presentation.slides.all().order_by("position"))
    theme = presentation.theme

    exporter = get_exporter(format)
    result = exporter.export(presentation, slides, theme)
    return ServiceResult.ok(data=result)
