from apps.ai.dtos import GenerationRequest


def build_system_prompt(request: GenerationRequest) -> str:
    return (
        f"You are a presentation expert. Generate {request.num_slides} slides "
        f"about '{request.topic}' in a {request.style} style. "
        f"Return structured JSON with heading, body, and notes for each slide."
    )


def build_user_prompt(request: GenerationRequest) -> str:
    base = f"Create a {request.num_slides}-slide presentation about: {request.topic}"
    if request.additional_instructions:
        base += f"\n\nAdditional instructions: {request.additional_instructions}"
    return base
