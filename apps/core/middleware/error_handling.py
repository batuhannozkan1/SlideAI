from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.core.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

EXCEPTION_STATUS_MAP = {
    NotFoundError: 404,
    PermissionDeniedError: 403,
    ValidationError: 400,
    ConflictError: 409,
}


class DomainExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_exception(
        self, request: HttpRequest, exception: Exception
    ) -> HttpResponse | None:
        # API requests get JSON errors from DRF's exception handler, never an
        # HTML error page. This guard keeps SSR error templates for the web app
        # while letting domain exceptions on /api/ paths surface as JSON.
        if request.path.startswith("/api/"):
            return None
        for exc_class, status_code in EXCEPTION_STATUS_MAP.items():
            if isinstance(exception, exc_class):
                template = f"errors/{status_code}.html"
                return render(
                    request,
                    template,
                    {"message": str(exception)},
                    status=status_code,
                )
        return None
