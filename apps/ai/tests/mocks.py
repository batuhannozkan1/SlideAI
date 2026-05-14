from apps.ai.clients.base_client import BaseAIClient
from apps.ai.dtos import GenerationRequest, GenerationResult, SlideContent


class MockAIClient(BaseAIClient):
    def generate(self, request: GenerationRequest) -> GenerationResult:
        slides = tuple(
            SlideContent(
                heading=f"Slide {i + 1}: {request.topic}",
                body=f"Content for slide {i + 1}",
                notes=f"Notes for slide {i + 1}",
            )
            for i in range(request.num_slides)
        )
        return GenerationResult(
            slides=slides,
            model_used="mock",
            token_count=0,
        )
