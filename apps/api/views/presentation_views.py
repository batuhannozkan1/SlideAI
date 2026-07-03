"""Presentation endpoints — thin adapters over presentation_service / slide_service."""
from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.presentations.dtos import CreatePresentationDTO, UpdatePresentationDTO
from apps.presentations.services import presentation_service, slide_service

from ..pagination import paginated_response
from ..serializers import (
    PresentationCreateSerializer,
    PresentationSerializer,
    PresentationUpdateSerializer,
    SlideSerializer,
)


def _presentation_with_slides(presentation, slides) -> dict:
    data = PresentationSerializer(presentation).data
    data["slides"] = SlideSerializer(slides, many=True).data
    return data


class PresentationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            page = int(request.query_params.get("page", 1))
        except (TypeError, ValueError):
            page = 1
        try:
            page_size = int(request.query_params.get("page_size", 20))
        except (TypeError, ValueError):
            page_size = 20
        page = max(1, page)
        page_size = max(1, min(page_size, 100))

        result = presentation_service.list_user_presentations(
            owner_id=request.user.id, page=page, page_size=page_size
        )
        return paginated_response(result, PresentationSerializer)

    def post(self, request):
        serializer = PresentationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        v = serializer.validated_data
        dto = CreatePresentationDTO(
            title=v["title"],
            description=v.get("description", ""),
            owner_id=request.user.id,
            theme_id=v.get("theme_id"),
        )
        result = presentation_service.create_presentation(dto)
        return Response(PresentationSerializer(result.data).data, status=201)


class PresentationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        result = presentation_service.get_presentation(
            pk, requesting_user_id=request.user.id
        )
        slides = slide_service.list_slides(pk).data
        return Response(_presentation_with_slides(result.data, slides))

    def patch(self, request, pk):
        serializer = PresentationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        v = serializer.validated_data
        dto = UpdatePresentationDTO(
            title=v.get("title"),
            description=v.get("description"),
            theme_id=v.get("theme_id"),
            is_public=v.get("is_public"),
        )
        result = presentation_service.update_presentation(
            pk, dto, requesting_user_id=request.user.id
        )
        return Response(PresentationSerializer(result.data).data)

    def delete(self, request, pk):
        presentation_service.delete_presentation(
            pk, requesting_user_id=request.user.id
        )
        return Response(status=204)


class PresentationDuplicateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        result = presentation_service.duplicate_presentation(
            pk, requesting_user_id=request.user.id
        )
        return Response(PresentationSerializer(result.data).data, status=201)
