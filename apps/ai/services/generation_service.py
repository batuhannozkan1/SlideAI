from apps.ai.clients.base_client import BaseAIClient
from apps.ai.dtos import GenerationRequest, GenerationResult


def generate_slides(
    client: BaseAIClient,
    request: GenerationRequest,
) -> GenerationResult:
    return client.generate(request)
