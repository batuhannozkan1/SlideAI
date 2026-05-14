from __future__ import annotations

from apps.accounts.models import User
from apps.core.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def get_by_username(self, username: str) -> User | None:
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def email_exists(self, email: str) -> bool:
        return User.objects.filter(email=email).exists()
