from __future__ import annotations

import json

from apps.ai.dtos import GenerationRequest
from apps.ai.prompts.slide_generation import (
    FREE_FORM_ADDITION,
    LAYOUT_OPTIONS,
    SLIDE_GENERATION_SYSTEM,
    SLIDE_JSON_SCHEMA,
    TEMPLATE_GUIDED_ADDITION,
)

LANGUAGE_MAP = {
    "tr": "Turkish",
    "en": "English",
}


def build_system_prompt(request: GenerationRequest) -> str:
    language = LANGUAGE_MAP.get(request.language, request.language)

    prompt = SLIDE_GENERATION_SYSTEM.format(
        json_schema=SLIDE_JSON_SCHEMA,
        layouts=LAYOUT_OPTIONS,
        language=language,
        style=request.style,
        num_slides=request.num_slides,
    )

    if request.template_structure:
        slides_spec = request.template_structure.get("slides", [])
        structure_text = json.dumps(slides_spec, indent=2, ensure_ascii=False)
        prompt += TEMPLATE_GUIDED_ADDITION.format(template_structure=structure_text)
    else:
        prompt += FREE_FORM_ADDITION

    return prompt


def build_user_prompt(request: GenerationRequest) -> str:
    prompt = f"Create a {request.num_slides}-slide presentation about: {request.topic}"

    if request.additional_instructions:
        prompt += f"\n\nAdditional instructions: {request.additional_instructions}"

    return prompt
