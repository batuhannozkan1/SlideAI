from .ai_serializers import AIGenerateSerializer, AISlideEditSerializer
from .auth_serializers import LoginSerializer, MeSerializer, RegisterSerializer, UserSerializer
from .dashboard_serializers import DashboardStatsSerializer
from .presentation_serializers import (
    PresentationCreateSerializer,
    PresentationSerializer,
    PresentationUpdateSerializer,
)
from .slide_serializers import (
    SlideCreateSerializer,
    SlideReorderSerializer,
    SlideSerializer,
    SlideUpdateSerializer,
)
from .theme_serializers import TemplateSerializer, ThemeSerializer

__all__ = [
    "AIGenerateSerializer",
    "AISlideEditSerializer",
    "LoginSerializer",
    "MeSerializer",
    "RegisterSerializer",
    "UserSerializer",
    "DashboardStatsSerializer",
    "PresentationCreateSerializer",
    "PresentationSerializer",
    "PresentationUpdateSerializer",
    "SlideCreateSerializer",
    "SlideReorderSerializer",
    "SlideSerializer",
    "SlideUpdateSerializer",
    "TemplateSerializer",
    "ThemeSerializer",
]
