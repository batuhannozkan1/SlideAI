from __future__ import annotations

from apps.accounts.repositories import profile_repo
from apps.core.dtos import ServiceResult
from apps.core.exceptions import NotFoundError


def get_profile(user_id: int) -> ServiceResult:
    profile = profile_repo.get_by_user_id(user_id)
    if profile is None:
        raise NotFoundError("UserProfile", user_id)
    return ServiceResult.ok(data=profile)


def update_profile(user_id: int, *, bio: str | None = None, avatar_url: str | None = None) -> ServiceResult:
    profile = profile_repo.get_by_user_id(user_id)
    if profile is None:
        raise NotFoundError("UserProfile", user_id)

    update_fields = {
        k: v
        for k, v in {"bio": bio, "avatar_url": avatar_url}.items()
        if v is not None
    }

    if not update_fields:
        return ServiceResult.ok(data=profile)

    updated = profile_repo.update(profile, **update_fields)
    return ServiceResult.ok(data=updated)
