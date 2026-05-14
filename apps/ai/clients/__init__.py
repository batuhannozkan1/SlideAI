from __future__ import annotations

from typing import Type

from django.conf import settings

from apps.ai.clients.base_client import BaseAIClient

_registry: dict[str, Type[BaseAIClient]] = {}


def register_client(name: str, client_class: Type[BaseAIClient]) -> None:
    _registry[name] = client_class


def get_ai_client() -> BaseAIClient:
    provider = getattr(settings, "AI_PROVIDER", "")

    if not provider:
        raise RuntimeError(
            "AI_PROVIDER is not configured. Set it in your .env file."
        )

    if provider not in _registry:
        available = ", ".join(_registry.keys()) or "none"
        raise RuntimeError(
            f"Unknown AI provider: '{provider}'. Available: {available}"
        )

    return _registry[provider]()


def _auto_discover() -> None:
    provider = getattr(settings, "AI_PROVIDER", "")
    if provider == "together":
        from apps.ai.clients import together_client  # noqa: F401
    elif provider == "mock":
        from apps.ai.tests import mocks  # noqa: F401


_auto_discover()
