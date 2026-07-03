from apps.accounts.models import User
from apps.presentations.models import Presentation, Slide


def create_test_user(**kwargs) -> User:
    defaults = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
    }
    defaults.update(kwargs)
    return User.objects.create_user(**defaults)


def create_test_presentation(owner: User, **kwargs) -> Presentation:
    defaults = {
        "title": "Test Presentation",
        "description": "A test presentation",
        "owner": owner,
    }
    defaults.update(kwargs)
    return Presentation.objects.create(**defaults)


def create_test_slide(presentation: Presentation, **kwargs) -> Slide:
    defaults = {
        "presentation": presentation,
        "heading": "Test Slide",
        "slide_type": "split",
        "content": {"subtitle": "Test subtitle", "points": []},
        "position": 0,
    }
    defaults.update(kwargs)
    return Slide.objects.create(**defaults)
