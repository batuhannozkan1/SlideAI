from __future__ import annotations

from django.conf import settings

from apps.ai.clients.base_client import BaseAIClient


def get_ai_client() -> BaseAIClient:
    provider = getattr(settings, "AI_PROVIDER", "")

    if not provider:
        raise RuntimeError(
            "AI_PROVIDER is not configured. Set it in your .env file."
        )

    raise RuntimeError(
        f"Unknown AI provider: '{provider}'. "
        f"Create a concrete client in apps/ai/clients/ and register it here."
    )
