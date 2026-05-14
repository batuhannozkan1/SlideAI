from __future__ import annotations

import logging

from apps.ai.clients import get_ai_client
from apps.ai.dtos import GenerationRequest, GenerationResult
from apps.core.dtos import ServiceResult
from apps.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


def generate_presentation_slides(request: GenerationRequest) -> ServiceResult:
    try:
        client = get_ai_client()
        result = client.generate(request)
    except ExternalServiceError:
        raise
    except Exception as exc:
        logger.error("Unexpected AI generation error: %s", exc)
        raise ExternalServiceError("Slayt üretimi sırasında beklenmeyen bir hata oluştu.") from exc

    errors = _validate_generation(result, request.num_slides)
    if errors:
        return ServiceResult.fail({"generation": errors})

    return ServiceResult.ok(data=result)


def regenerate_single_slide(
    topic: str,
    slide_context: str,
    style: str = "professional",
    language: str = "tr",
) -> ServiceResult:
    request = GenerationRequest(
        topic=topic,
        num_slides=1,
        style=style,
        additional_instructions=(
            f"Regenerate ONLY ONE slide. Context of surrounding slides:\n{slide_context}\n"
            "Generate a single fresh slide that fits this context."
        ),
        language=language,
    )

    try:
        client = get_ai_client()
        result = client.generate(request)
    except ExternalServiceError:
        raise
    except Exception as exc:
        logger.error("Unexpected AI regeneration error: %s", exc)
        raise ExternalServiceError("Slayt yeniden üretimi sırasında hata oluştu.") from exc

    if not result.slides:
        return ServiceResult.fail({"generation": ["AI yanıtında slayt bulunamadı."]})

    return ServiceResult.ok(data=result.slides[0])


def _validate_generation(result: GenerationResult, expected_count: int) -> list[str]:
    errors: list[str] = []

    if not result.slides:
        errors.append("AI herhangi bir slayt üretmedi.")
        return errors

    for i, slide in enumerate(result.slides):
        if not slide.heading.strip():
            errors.append(f"Slayt {i + 1}: başlık boş.")
        if not slide.body.strip():
            errors.append(f"Slayt {i + 1}: içerik boş.")

    return errors
