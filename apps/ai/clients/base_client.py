from __future__ import annotations

from abc import ABC, abstractmethod

from apps.ai.dtos import GenerationRequest, GenerationResult


class BaseAIClient(ABC):
    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult: ...
