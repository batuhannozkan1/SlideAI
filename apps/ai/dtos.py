from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GenerationRequest:
    topic: str
    num_slides: int
    style: str = "professional"
    additional_instructions: str = ""
    template_structure: dict[str, Any] | None = None
    language: str = "tr"


@dataclass(frozen=True)
class SlideContent:
    heading: str
    body: str
    notes: str = ""
    layout: str = "content"


@dataclass(frozen=True)
class GenerationResult:
    slides: tuple[SlideContent, ...]
    title_suggestion: str = ""
    model_used: str = ""
    token_count: int = 0
