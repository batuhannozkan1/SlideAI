from __future__ import annotations

from typing import Sequence
from uuid import UUID

from apps.core.dtos import ServiceResult
from apps.core.exceptions import NotFoundError, PermissionDeniedError
from apps.presentations.dtos import CreateSlideDTO, UpdateSlideDTO
from apps.presentations.repositories import presentation_repo, slide_repo


def get_slide(slide_id: UUID, *, requesting_user_id: int) -> ServiceResult:
    slide = slide_repo.get_by_id_or_raise(slide_id)
    presentation = presentation_repo.get_by_id_or_raise(slide.presentation_id)

    if presentation.owner_id != requesting_user_id:
        raise PermissionDeniedError("You do not own this presentation.")

    return ServiceResult.ok(data=slide)


def create_slide(dto: CreateSlideDTO, *, requesting_user_id: int) -> ServiceResult:
    presentation = presentation_repo.get_by_id_or_raise(dto.presentation_id)

    if presentation.owner_id != requesting_user_id:
        raise PermissionDeniedError("You do not own this presentation.")

    position = dto.position
    if position < 0:
        position = slide_repo.get_max_position(dto.presentation_id) + 1

    slide = slide_repo.create(
        presentation_id=dto.presentation_id,
        heading=dto.heading,
        body=dto.body,
        notes=dto.notes,
        layout=dto.layout,
        position=position,
    )

    presentation_repo.update(presentation, slide_count=presentation.slide_count + 1)

    return ServiceResult.ok(data=slide)


def update_slide(
    slide_id: UUID,
    dto: UpdateSlideDTO,
    *,
    requesting_user_id: int,
) -> ServiceResult:
    slide = slide_repo.get_by_id_or_raise(slide_id)
    presentation = presentation_repo.get_by_id_or_raise(slide.presentation_id)

    if presentation.owner_id != requesting_user_id:
        raise PermissionDeniedError("You do not own this presentation.")

    update_fields = {
        k: v
        for k, v in {
            "heading": dto.heading,
            "body": dto.body,
            "notes": dto.notes,
            "layout": dto.layout,
        }.items()
        if v is not None
    }

    if not update_fields:
        return ServiceResult.ok(data=slide)

    updated = slide_repo.update(slide, **update_fields)
    return ServiceResult.ok(data=updated)


def delete_slide(slide_id: UUID, *, requesting_user_id: int) -> ServiceResult:
    slide = slide_repo.get_by_id_or_raise(slide_id)
    presentation = presentation_repo.get_by_id_or_raise(slide.presentation_id)

    if presentation.owner_id != requesting_user_id:
        raise PermissionDeniedError("You do not own this presentation.")

    slide_repo.delete(slide)
    presentation_repo.update(presentation, slide_count=max(0, presentation.slide_count - 1))

    return ServiceResult.ok()


def reorder_slides(
    presentation_id: UUID,
    slide_ids: Sequence[UUID],
    *,
    requesting_user_id: int,
) -> ServiceResult:
    presentation = presentation_repo.get_by_id_or_raise(presentation_id)

    if presentation.owner_id != requesting_user_id:
        raise PermissionDeniedError("You do not own this presentation.")

    slide_repo.reorder(slide_ids)
    return ServiceResult.ok()


def list_slides(presentation_id: UUID) -> ServiceResult:
    slides = slide_repo.list_by_presentation(presentation_id)
    return ServiceResult.ok(data=slides)
