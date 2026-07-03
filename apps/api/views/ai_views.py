"""AI endpoints: synchronous generation and single-slide AI edit.

Generation can take 10-30s (upstream LLM call). The orchestration mirrors the
SSR ``presentation_generate`` view: generate → create presentation → create each
slide → return the full presentation with slides.
"""
from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai.dtos import GenerationRequest
from apps.ai.services.generation_service import (
    edit_slide_with_instruction,
    generate_presentation_slides,
)
from apps.presentations.dtos import CreatePresentationDTO, CreateSlideDTO, UpdateSlideDTO
from apps.presentations.services import presentation_service, slide_service, template_service

from ..serializers import AIGenerateSerializer, AISlideEditSerializer, SlideSerializer
from .presentation_views import _presentation_with_slides


class GenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AIGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        v = serializer.validated_data

        template_structure = None
        if v.get("template_id"):
            template = template_service.get_template(v["template_id"]).data
            template_structure = template.structure

        gen_request = GenerationRequest(
            topic=v["topic"],
            num_slides=v["num_slides"],
            style=v["style"],
            additional_instructions=v.get("additional_instructions", ""),
            template_structure=template_structure,
            language=v["language"],
        )

        gen = generate_presentation_slides(gen_request)
        if not gen.success:
            return Response({"errors": gen.errors}, status=400)

        gen_result = gen.data
        pres_dto = CreatePresentationDTO(
            title=gen_result.title_suggestion or v["topic"],
            description=f"AI ile oluşturuldu: {v['topic']}",
            owner_id=request.user.id,
            theme_id=v.get("theme_id"),
        )
        presentation = presentation_service.create_presentation(pres_dto).data

        for i, slide_content in enumerate(gen_result.slides):
            slide_service.create_slide(
                CreateSlideDTO(
                    presentation_id=presentation.pk,
                    heading=slide_content.heading,
                    notes=slide_content.notes,
                    slide_type=slide_content.slide_type,
                    content=slide_content.content,
                    position=i,
                ),
                requesting_user_id=request.user.id,
            )

        # Re-fetch so slide_count (bumped per-slide in the service) is current.
        fresh = presentation_service.get_presentation(
            presentation.pk, requesting_user_id=request.user.id
        ).data
        slides = slide_service.list_slides(presentation.pk).data
        return Response(_presentation_with_slides(fresh, slides), status=201)


class SlideEditView(APIView):
    """Apply a natural-language instruction to one slide and persist the result."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = AISlideEditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        v = serializer.validated_data

        slide = slide_service.get_slide(pk, requesting_user_id=request.user.id).data
        presentation = presentation_service.get_presentation(
            slide.presentation_id, requesting_user_id=request.user.id
        ).data
        outline = tuple(
            s.heading for s in slide_service.list_slides(presentation.pk).data
        )
        history = tuple(
            (str(m.get("role", "")), str(m.get("text", "")))
            for m in v.get("history", [])
            if isinstance(m, dict) and m.get("role") in ("user", "assistant")
        )[-8:]

        result = edit_slide_with_instruction(
            slide_type=slide.slide_type,
            heading=slide.heading,
            content=slide.content or {},
            instruction=v["instruction"],
            presentation_title=presentation.title,
            outline=outline,
            history=history,
            change_topic=v["change_topic"],
        )
        if not result.success:
            return Response({"errors": result.errors}, status=400)

        edited = result.data.slide
        updated = slide_service.update_slide(
            pk,
            UpdateSlideDTO(
                heading=edited.heading,
                slide_type=edited.slide_type,
                content=edited.content,
            ),
            requesting_user_id=request.user.id,
        ).data
        return Response(
            {"slide": SlideSerializer(updated).data, "message": result.data.message}
        )
