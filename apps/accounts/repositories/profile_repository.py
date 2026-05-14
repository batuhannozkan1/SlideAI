from __future__ import annotations

from apps.accounts.models import UserProfile
from apps.core.base_repository import BaseRepository


class ProfileRepository(BaseRepository[UserProfile]):
    model = UserProfile

    def get_by_user_id(self, user_id: int) -> UserProfile | None:
        try:
            return UserProfile.objects.select_related("user").get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return None
