from __future__ import annotations

import json

from apps.ai.dtos import GenerationRequest, SlideEditRequest
from apps.ai.prompts.slide_generation import (
    FREE_FORM_ADDITION,
    SLIDE_EDIT_SYSTEM,
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


def build_edit_system_prompt(request: SlideEditRequest) -> str:
    language = LANGUAGE_MAP.get(request.language, request.language)
    return SLIDE_EDIT_SYSTEM.format(json_schema=SLIDE_JSON_SCHEMA, language=language)


def build_edit_user_prompt(request: SlideEditRequest) -> str:
    slide_json = json.dumps(
        {
            "heading": request.heading,
            "slide_type": request.slide_type,
            "content": request.content,
        },
        ensure_ascii=False,
        indent=2,
    )
    parts = [
        "PRESENTATION SUBJECT (authoritative — this slide MUST be about this, in {lang}):".format(
            lang=LANGUAGE_MAP.get(request.language, request.language)
        ),
        f'  "{request.presentation_title}"',
    ]
    if request.outline:
        parts.append(
            "\nAll slide headings in the deck (for flow / to avoid repeating other slides):\n"
            + "\n".join(request.outline)
        )
    parts.append(
        "\nCURRENT slide — this is the existing DRAFT you are improving (do NOT just keep it as-is "
        "if it drifted off-subject; bring it back to the subject above):\n" + slide_json
    )
    parts.append(
        "\nUSER INSTRUCTION (how to change the current slide — interpret it in service of the "
        f"subject above, never as a new subject):\n{request.instruction}"
    )
    return "\n".join(parts)
