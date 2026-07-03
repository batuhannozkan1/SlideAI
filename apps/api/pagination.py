"""Helpers to render a service-layer ``PaginatedResult`` as a JSON envelope.

The services already paginate and return a frozen ``PaginatedResult`` DTO, so
the API does not use DRF's own pagination classes — it just serializes the DTO's
items and attaches the page metadata.
"""
from __future__ import annotations

from typing import Type

from rest_framework.response import Response
from rest_framework.serializers import Serializer

from apps.core.dtos import PaginatedResult


def paginated_response(result: PaginatedResult, item_serializer: Type[Serializer]) -> Response:
    return Response(
        {
            "results": item_serializer(result.items, many=True).data,
            "pagination": {
                "total_count": result.total_count,
                "page": result.page,
                "page_size": result.page_size,
                "total_pages": result.total_pages,
                "has_next": result.has_next,
                "has_previous": result.has_previous,
            },
        }
    )
