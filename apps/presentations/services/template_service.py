from __future__ import annotations

from uuid import UUID

from apps.core.dtos import ServiceResult
from apps.core.exceptions import NotFoundError
from apps.presentations.repositories import template_repo


def list_templates() -> ServiceResult:
    templates = template_repo.list_active()
    return ServiceResult.ok(data=templates)


def get_template(template_id: UUID) -> ServiceResult:
    template = template_repo.get_by_id(template_id)
    if template is None:
        raise NotFoundError("SlideTemplate", template_id)
    return ServiceResult.ok(data=template)
