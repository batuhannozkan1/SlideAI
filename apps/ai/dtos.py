from __future__ import annotations

from dataclasses import dataclass, field
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
    slide_type: str = "split"
    content: dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass(frozen=True)
class GenerationResult:
    slides: tuple[SlideContent, ...]
    title_suggestion: str = ""
    model_used: str = ""
    token_count: int = 0


@dataclass(frozen=True)
class SlideEditRequest:
    slide_type: str
    heading: str
    content: dict[str, Any]
    instruction: str
    presentation_title: str = ""
    outline: tuple[str, ...] = ()  # headings of all slides in order (for context)
    history: tuple[tuple[str, str], ...] = ()  # prior chat turns: (role, text)
    language: str = "tr"


@dataclass(frozen=True)
class SlideEditResult:
    slide: SlideContent
    message: str = ""


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class AgentStep:
    text: str
    tool_calls: tuple[ToolCall, ...]
    assistant_message: dict[str, Any]  # raw assistant message to append back to the thread


@dataclass(frozen=True)
class AgentResult:
    message: str
    changed: bool = False
    steps: int = 0
