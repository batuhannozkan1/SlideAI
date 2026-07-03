"""Slide endpoints — thin adapters over slide_service.

List/create are nested under a presentation; detail/update/delete address a slide
by its own id. Ownership checks live in the service layer (→ 403/404 JSON).
"""
from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.presentations.dtos import CreateSlideDTO, UpdateSlideDTO
from apps.presentations.services import presentation_service, slide_service

from ..serializers import (
    SlideCreateSerializer,
    SlideReorderSerializer,
    SlideSerializer,
    SlideUpdateSerializer,
)


class SlideListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Ownership / public-access check via the presentation service.
        presentation_service.get_presentation(pk, requesting_user_id=request.user.id)
        slides = slide_service.list_slides(pk).data
        return Response({"results": SlideSerializer(slides, many=True).data})

    def post(self, request, pk):
        serializer = SlideCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        v = serializer.validated_data
        dto = CreateSlideDTO(
            presentation_id=pk,
            heading=v["heading"],
            position=v["position"],
            notes=v["notes"],
            slide_type=v["slide_type"],
            content=v["content"],
        )
        result = slide_service.create_slide(dto, requesting_user_id=request.user.id)
        return Response(SlideSerializer(result.data).data, status=201)


class SlideReorderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = SlideReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slide_service.reorder_slides(
            pk,
            serializer.validated_data["slide_ids"],
            requesting_user_id=request.user.id,
        )
        return Response({"status": "ok"})


class SlideDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        result = slide_service.get_slide(pk, requesting_user_id=request.user.id)
        return Response(SlideSerializer(result.data).data)

    def patch(self, request, pk):
        serializer = SlideUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        v = serializer.validated_data
        dto = UpdateSlideDTO(
            heading=v.get("heading"),
            notes=v.get("notes"),
            slide_type=v.get("slide_type"),
            content=v.get("content"),
        )
        result = slide_service.update_slide(
            pk, dto, requesting_user_id=request.user.id
        )
        return Response(SlideSerializer(result.data).data)

    def delete(self, request, pk):
        slide_service.delete_slide(pk, requesting_user_id=request.user.id)
        return Response(status=204)
