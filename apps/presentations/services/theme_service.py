from __future__ import annotations

from uuid import UUID

from apps.core.dtos import ServiceResult
from apps.core.exceptions import NotFoundError, PermissionDeniedError
from apps.presentations.repositories import presentation_repo, theme_repo


def list_active_themes() -> ServiceResult:
    themes = theme_repo.list_active()
    return ServiceResult.ok(data=list(themes))


def get_theme(theme_id: UUID) -> ServiceResult:
    theme = theme_repo.get_by_id(theme_id)
    if theme is None:
        raise NotFoundError("Theme", theme_id)
    return ServiceResult.ok(data=theme)


def apply_theme(
    presentation_id: UUID,
    theme_id: UUID | None,
    *,
    user_id: int,
) -> ServiceResult:
    presentation = presentation_repo.get_by_id_or_raise(presentation_id)

    if presentation.owner_id != user_id:
        raise PermissionDeniedError("Bu sunuma erişim izniniz yok.")

    if theme_id:
        theme = theme_repo.get_by_id(theme_id)
        if theme is None:
            raise NotFoundError("Theme", theme_id)

    presentation_repo.update(presentation, theme_id=theme_id)
    return ServiceResult.ok()
