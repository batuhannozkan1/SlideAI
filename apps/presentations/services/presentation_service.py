from __future__ import annotations

from uuid import UUID

from apps.core.dtos import PaginatedResult, ServiceResult
from apps.core.exceptions import NotFoundError, PermissionDeniedError
from apps.presentations.dtos import CreatePresentationDTO, UpdatePresentationDTO
from apps.presentations.repositories import presentation_repo


def create_presentation(dto: CreatePresentationDTO) -> ServiceResult:
    presentation = presentation_repo.create(
        title=dto.title,
        description=dto.description,
        owner_id=dto.owner_id,
        theme_id=dto.theme_id,
    )
    return ServiceResult.ok(data=presentation)


def get_presentation(presentation_id: UUID, *, requesting_user_id: int) -> ServiceResult:
    presentation = presentation_repo.get_with_slides(presentation_id)

    if presentation is None:
        raise NotFoundError("Presentation", presentation_id)

    if presentation.owner_id != requesting_user_id and not presentation.is_public:
        raise PermissionDeniedError("You do not have access to this presentation.")

    return ServiceResult.ok(data=presentation)


def list_user_presentations(
    owner_id: int, *, page: int = 1, page_size: int = 20
) -> PaginatedResult:
    offset = (page - 1) * page_size
    items = presentation_repo.list_by_owner(owner_id, limit=page_size, offset=offset)
    total = presentation_repo.count(owner_id=owner_id, is_deleted=False)

    return PaginatedResult(
        items=items,
        total_count=total,
        page=page,
        page_size=page_size,
    )


def update_presentation(
    presentation_id: UUID,
    dto: UpdatePresentationDTO,
    *,
    requesting_user_id: int,
) -> ServiceResult:
    presentation = presentation_repo.get_by_id_or_raise(presentation_id)

    if presentation.owner_id != requesting_user_id:
        raise PermissionDeniedError("You do not own this presentation.")

    update_fields = {
        k: v
        for k, v in {
            "title": dto.title,
            "description": dto.description,
            "theme_id": dto.theme_id,
            "is_public": dto.is_public,
        }.items()
        if v is not None
    }

    if not update_fields:
        return ServiceResult.ok(data=presentation)

    updated = presentation_repo.update(presentation, **update_fields)
    return ServiceResult.ok(data=updated)


def delete_presentation(
    presentation_id: UUID, *, requesting_user_id: int
) -> ServiceResult:
    presentation = presentation_repo.get_by_id_or_raise(presentation_id)

    if presentation.owner_id != requesting_user_id:
        raise PermissionDeniedError("You do not own this presentation.")

    presentation_repo.soft_delete(presentation)
    return ServiceResult.ok()


def duplicate_presentation(
    presentation_id: UUID, *, requesting_user_id: int
) -> ServiceResult:
    from apps.presentations.repositories import slide_repo

    source = presentation_repo.get_with_slides(presentation_id)
    if source is None:
        raise NotFoundError("Presentation", presentation_id)

    if source.owner_id != requesting_user_id and not source.is_public:
        raise PermissionDeniedError("Bu sunuma erişim izniniz yok.")

    copy = presentation_repo.create(
        title=f"{source.title} (Kopya)",
        description=source.description,
        owner_id=requesting_user_id,
        theme_id=source.theme_id,
    )

    slides = list(source.slides.all().order_by("position"))
    for slide in slides:
        slide_repo.create(
            presentation_id=copy.pk,
            heading=slide.heading,
            body=slide.body,
            notes=slide.notes,
            layout=slide.layout,
            position=slide.position,
        )

    presentation_repo.update(copy, slide_count=len(slides))
    return ServiceResult.ok(data=copy)
