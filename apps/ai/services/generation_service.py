from __future__ import annotations

import logging
from dataclasses import replace

from apps.ai.clients import get_ai_client
from apps.ai.dtos import (
    GenerationRequest,
    GenerationResult,
    SlideEditRequest,
    SlideEditResult,
)
from apps.core.dtos import ServiceResult
from apps.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


def generate_presentation_slides(request: GenerationRequest) -> ServiceResult:
    result = _call_client(request)

    errors = _validate_generation(result)
    if errors:
        return ServiceResult.fail({"generation": errors})

    if len(result.slides) != request.num_slides:
        logger.info(
            "AI produced %d slides for a target of %d (count is a soft target).",
            len(result.slides), request.num_slides,
        )
    _log_structure_warnings(result)
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

    result = _call_client(request)
    if not result.slides:
        return ServiceResult.fail({"generation": ["AI yanıtında slayt bulunamadı."]})

    return ServiceResult.ok(data=result.slides[0])


def edit_slide_with_instruction(
    *,
    slide_type: str,
    heading: str,
    content: dict,
    instruction: str,
    presentation_title: str = "",
    outline: tuple[str, ...] = (),
    history: tuple[tuple[str, str], ...] = (),
    change_topic: bool = False,
    language: str = "tr",
) -> ServiceResult:
    """Apply a natural-language instruction to a single slide via the AI assistant.
    The presentation title + outline give the assistant the deck's overall context;
    history carries prior chat turns for multi-turn coherence."""
    request = SlideEditRequest(
        slide_type=slide_type,
        heading=heading,
        content=content or {},
        instruction=instruction,
        presentation_title=presentation_title,
        outline=outline,
        history=history,
        language=language,
    )
    try:
        client = get_ai_client()
        result = client.edit_slide(request)
    except ExternalServiceError:
        raise
    except Exception as exc:
        logger.error("Unexpected AI edit error: %s", exc)
        raise ExternalServiceError(
            "Slayt düzenleme sırasında beklenmeyen bir hata oluştu."
        ) from exc

    slide = result.slide
    if slide.slide_type not in {"cover", "split", "closing"}:
        return ServiceResult.fail({"edit": ["Geçersiz slayt tipi üretildi."]})

    # Deterministic topic lock: when editing an EXISTING slide (non-empty original
    # heading) and the caller did not signal a topic change, keep the original heading
    # whatever the model returns. The DECISION (change topic or not) is made dynamically
    # by the agent/caller via `change_topic`; the code only enforces it.
    if heading.strip() and not change_topic:
        if slide.heading != heading:
            slide = replace(slide, heading=heading)
            result = SlideEditResult(slide=slide, message=result.message)
    elif not slide.heading.strip():
        return ServiceResult.fail({"edit": ["Düzenlenen slaytın başlığı boş kaldı."]})

    return ServiceResult.ok(data=result)


# --- internals ---------------------------------------------------------------


def _call_client(request: GenerationRequest) -> GenerationResult:
    try:
        client = get_ai_client()
        return client.generate(request)
    except ExternalServiceError:
        raise
    except Exception as exc:
        logger.error("Unexpected AI generation error: %s", exc)
        raise ExternalServiceError(
            "Slayt üretimi sırasında beklenmeyen bir hata oluştu."
        ) from exc


def _log_structure_warnings(result: GenerationResult) -> None:
    if not result.slides:
        return
    if result.slides[0].slide_type != "cover":
        logger.warning(
            "First slide type is '%s', expected 'cover'.", result.slides[0].slide_type
        )
    if len(result.slides) > 1 and result.slides[-1].slide_type != "closing":
        logger.warning(
            "Last slide type is '%s', expected 'closing'.", result.slides[-1].slide_type
        )


def _validate_generation(result: GenerationResult) -> list[str]:
    """Quality/shape validation only — slide count is intentionally NOT enforced
    (a free count yields more coherent presentations than trimming/padding)."""
    errors: list[str] = []

    if not result.slides:
        errors.append("AI herhangi bir slayt üretmedi.")
        return errors

    valid_types = {"cover", "split", "closing"}
    for i, slide in enumerate(result.slides):
        if not slide.heading.strip():
            errors.append(f"Slayt {i + 1}: başlık boş.")
        if slide.slide_type not in valid_types:
            errors.append(f"Slayt {i + 1}: geçersiz slayt tipi '{slide.slide_type}'.")
        if slide.slide_type == "split":
            content = slide.content or {}
            if not content.get("points") and not content.get("visual"):
                errors.append(f"Slayt {i + 1}: içerik boş (madde veya görsel gerekli).")

    return errors
