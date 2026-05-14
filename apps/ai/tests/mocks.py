from apps.ai.clients import register_client
from apps.ai.clients.base_client import BaseAIClient
from apps.ai.dtos import GenerationRequest, GenerationResult, SlideContent


class MockAIClient(BaseAIClient):
    def generate(self, request: GenerationRequest) -> GenerationResult:
        slides = tuple(
            SlideContent(
                heading=f"Slayt {i + 1}: {request.topic}",
                body=f"Bu slaytın içeriği: {request.topic} hakkında detaylı bilgi.",
                notes=f"Konuşmacı notu: {request.topic} - slayt {i + 1}",
                layout="title" if i == 0 else "content",
            )
            for i in range(request.num_slides)
        )
        return GenerationResult(
            slides=slides,
            title_suggestion=request.topic,
            model_used="mock",
            token_count=0,
        )


register_client("mock", MockAIClient)
