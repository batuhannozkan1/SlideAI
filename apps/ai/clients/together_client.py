from __future__ import annotations

import json
import logging

import openai
from django.conf import settings

from apps.ai.clients import register_client
from apps.ai.clients.base_client import BaseAIClient
from apps.ai.dtos import GenerationRequest, GenerationResult, SlideContent
from apps.ai.services.prompt_service import build_system_prompt, build_user_prompt
from apps.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class TogetherClient(BaseAIClient):
    def __init__(self) -> None:
        self._client = openai.OpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL,
        )
        self._model = settings.AI_MODEL

    def generate(self, request: GenerationRequest) -> GenerationResult:
        system_prompt = build_system_prompt(request)
        user_prompt = build_user_prompt(request)

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=4096,
            )
        except openai.APIError as exc:
            logger.error("Together AI API error: %s", exc)
            raise ExternalServiceError(f"AI servisi hatası: {exc.message}") from exc

        raw = response.choices[0].message.content or "{}"
        model_used = response.model or self._model
        token_count = response.usage.total_tokens if response.usage else 0

        return _parse_response(raw, model_used, token_count)


def _parse_response(raw_json: str, model_used: str, token_count: int) -> GenerationResult:
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ExternalServiceError("AI yanıtı geçersiz JSON formatında.") from exc

    slides_data = data.get("slides", [])
    if not slides_data:
        raise ExternalServiceError("AI yanıtında slayt verisi bulunamadı.")

    slides = tuple(
        SlideContent(
            heading=s.get("heading", ""),
            body=s.get("body", ""),
            notes=s.get("notes", ""),
            layout=s.get("layout", "content"),
        )
        for s in slides_data
    )

    return GenerationResult(
        slides=slides,
        title_suggestion=data.get("title_suggestion", ""),
        model_used=model_used,
        token_count=token_count,
    )


register_client("together", TogetherClient)
