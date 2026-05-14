from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationRequest:
    topic: str
    num_slides: int
    style: str = "professional"
    additional_instructions: str = ""


@dataclass(frozen=True)
class SlideContent:
    heading: str
    body: str
    notes: str = ""
    layout: str = "content"


@dataclass(frozen=True)
class GenerationResult:
    slides: tuple[SlideContent, ...]
    model_used: str = ""
    token_count: int = 0
