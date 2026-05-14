from __future__ import annotations

from django.contrib.auth.hashers import make_password

from apps.accounts.repositories import profile_repo, user_repo
from apps.core.dtos import ServiceResult
from apps.core.exceptions import ConflictError, NotFoundError


def register_user(
    *,
    username: str,
    email: str,
    password: str,
) -> ServiceResult:
    if user_repo.email_exists(email):
        raise ConflictError(f"Email {email} is already registered.")

    user = user_repo.create(
        username=username,
        email=email,
        password=make_password(password),
    )
    profile_repo.create(user=user)

    return ServiceResult.ok(data=user)


def get_user(user_id: int) -> ServiceResult:
    user = user_repo.get_by_id(user_id)
    if user is None:
        raise NotFoundError("User", user_id)
    return ServiceResult.ok(data=user)
