from __future__ import annotations

from uuid import UUID


class SlideAIError(Exception):
    default_message = "An unexpected error occurred."

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(SlideAIError):
    def __init__(self, resource: str, identifier: UUID | int | str):
        super().__init__(f"{resource} with id={identifier} was not found.")
        self.resource = resource
        self.identifier = identifier


class PermissionDeniedError(SlideAIError):
    default_message = "You do not have permission to perform this action."


class ValidationError(SlideAIError):
    def __init__(self, errors: dict[str, list[str]]):
        self.errors = errors
        messages = "; ".join(
            f"{field}: {', '.join(msgs)}" for field, msgs in errors.items()
        )
        super().__init__(f"Validation failed: {messages}")


class ConflictError(SlideAIError):
    default_message = "This operation conflicts with the current state."


class ExternalServiceError(SlideAIError):
    default_message = "An external service is currently unavailable."
