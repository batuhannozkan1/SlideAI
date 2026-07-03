from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Any

from apps.ai.dtos import (
    AgentStep,
    GenerationRequest,
    GenerationResult,
    SlideEditRequest,
    SlideEditResult,
)


class BaseAIClient(ABC):
    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult: ...

    @abstractmethod
    def edit_slide(self, request: SlideEditRequest) -> SlideEditResult: ...

    @abstractmethod
    def complete_with_tools(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]],
        tool_choice: str = "auto",
    ) -> AgentStep: ...
