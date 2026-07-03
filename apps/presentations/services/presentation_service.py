from __future__ import annotations

from datetime import date, datetime, timedelta
from uuid import UUID

from django.utils import timezone

from apps.core.dtos import PaginatedResult, ServiceResult
from apps.core.exceptions import NotFoundError, PermissionDeniedError
from apps.presentations.dtos import CreatePresentationDTO, DashboardStatsDTO, UpdatePresentationDTO
from apps.presentations.repositories import presentation_repo

_MONTH_LABELS = (
    "Oca", "Şub", "Mar", "Nis", "May", "Haz",
    "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara",
)


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


def get_total_presentation_count(owner_id: int) -> int:
    return presentation_repo.count(owner_id=owner_id, is_deleted=False)


def get_dashboard_stats(owner_id: int) -> DashboardStatsDTO:
    total_presentations = presentation_repo.count(owner_id=owner_id, is_deleted=False)
    total_slides = presentation_repo.total_slide_count(owner_id)

    today = date.today()
    first_of_this_month = today.replace(day=1)
    first_of_last_month = (first_of_this_month - timedelta(days=1)).replace(day=1)

    def _aware(d: date) -> datetime:
        return timezone.make_aware(datetime(d.year, d.month, d.day))

    this_month = presentation_repo.count_created_since(owner_id, _aware(first_of_this_month))
    last_month_total = presentation_repo.count_created_since(owner_id, _aware(first_of_last_month))
    last_month = last_month_total - this_month

    if last_month > 0:
        growth = ((this_month - last_month) / last_month) * 100
    elif this_month > 0:
        growth = 100.0
    else:
        growth = 0.0

    draft_count = presentation_repo.count(owner_id=owner_id, is_deleted=False, is_public=False)
    published_count = presentation_repo.count(owner_id=owner_id, is_deleted=False, is_public=True)

    six_months_ago = first_of_this_month
    for _ in range(5):
        six_months_ago = (six_months_ago - timedelta(days=1)).replace(day=1)

    raw_counts = presentation_repo.count_created_per_month(owner_id, _aware(six_months_ago))
    count_map = {row["month"].date().replace(day=1): row["count"] for row in raw_counts}

    labels = []
    values = []
    cursor = six_months_ago
    for _ in range(6):
        labels.append(_MONTH_LABELS[cursor.month - 1])
        values.append(count_map.get(cursor, 0))
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1)

    chart_values = tuple(values)
    return DashboardStatsDTO(
        total_presentations=total_presentations,
        total_slides=total_slides,
        presentations_this_month=this_month,
        growth_percentage=round(growth, 1),
        draft_count=draft_count,
        published_count=published_count,
        chart_labels=tuple(labels),
        chart_values=chart_values,
        chart_max=max(chart_values) or 1,
    )


def get_recent_presentations(owner_id: int, *, limit: int = 5) -> tuple:
    return tuple(presentation_repo.list_by_owner(owner_id, limit=limit, offset=0))


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
            notes=slide.notes,
            slide_type=slide.slide_type,
            content=slide.content,
            position=slide.position,
        )

    presentation_repo.update(copy, slide_count=len(slides))
    return ServiceResult.ok(data=copy)
