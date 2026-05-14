from .presentation_repository import PresentationRepository
from .slide_repository import SlideRepository
from .template_repository import TemplateRepository
from .theme_repository import ThemeRepository

presentation_repo = PresentationRepository()
slide_repo = SlideRepository()
template_repo = TemplateRepository()
theme_repo = ThemeRepository()

__all__ = [
    "PresentationRepository",
    "SlideRepository",
    "TemplateRepository",
    "ThemeRepository",
    "presentation_repo",
    "slide_repo",
    "template_repo",
    "theme_repo",
]
