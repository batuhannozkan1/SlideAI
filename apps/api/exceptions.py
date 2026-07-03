"""Translate the project's domain exceptions into JSON API responses.

Registered as DRF's ``EXCEPTION_HANDLER`` so that exceptions raised inside the
service layer (which the API views call directly) surface as clean JSON with the
right status code — instead of the SSR HTML error pages produced by
``DomainExceptionMiddleware`` for the web app.
"""
from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_handler

from apps.core.exceptions import (
    ConflictError,
    ExternalServiceError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

# Ordered most-specific first; all are subclasses of SlideAIError.
_STATUS_MAP: tuple[tuple[type[Exception], int], ...] = (
    (NotFoundError, 404),
    (PermissionDeniedError, 403),
    (ValidationError, 400),
    (ConflictError, 409),
    (ExternalServiceError, 503),
)


def domain_exception_handler(exc, context):
    for exc_class, status_code in _STATUS_MAP:
        if isinstance(exc, exc_class):
            body: dict = {"detail": str(exc)}
            # ValidationError carries a structured field->messages mapping.
            errors = getattr(exc, "errors", None)
            if errors:
                body["errors"] = errors
            return Response(body, status=status_code)

    # Anything else (DRF's own ValidationError, auth errors, 500s) → DRF default.
    return drf_default_handler(exc, context)
