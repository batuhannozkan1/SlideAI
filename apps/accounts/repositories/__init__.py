from .profile_repository import ProfileRepository
from .user_repository import UserRepository

user_repo = UserRepository()
profile_repo = ProfileRepository()

__all__ = ["UserRepository", "ProfileRepository", "user_repo", "profile_repo"]
