import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.http import url_has_allowed_host_and_scheme

from apps.ai.services.generation_service import (
    edit_slide_with_instruction,
    regenerate_single_slide,
)
from apps.presentations.dtos import CreateSlideDTO, UpdateSlideDTO
from apps.presentations.forms.slide_forms import SlideForm
from apps.presentations.services import presentation_service, slide_service


def _starter_content(slide_type: str) -> dict:
    """A clean, non-empty default so a manually added slide renders properly
    (instead of a blank split card) and is ready to edit."""
    if slide_type == "cover":
        return {"eyebrow": "Bölüm", "subtitle": "Alt başlık",
                "description": "Açıklama metni.", "icon": "fa-presentation-screen", "date": "2026"}
    if slide_type == "closing":
        return {"eyebrow": "Kapanış", "subtitle": "Teşekkürler",
                "description": "Kapanış açıklaması.", "icon": "fa-circle-check", "stats": []}
    return {
        "eyebrow": "Bölüm",
        "subtitle": "Alt başlık — sağdaki İçerik sekmesinden veya Asistan'dan düzenleyin.",
        "points": [{"kind": "ok", "label": "Madde", "text": "Açıklama"}],
        "highlight": "",
        "visual": {"type": "dashboard", "data": {"cells": [{"value": "—", "label": "Etiket"}]}},
    }


def _render_slide_fragment(presentation, slide) -> str:
    slides = list(presentation.slides.all())
    return render_to_string(
        "presentations/slides/_slide.html",
        {
            "slide": slide,
            "page": slide.position + 1,
            "total": len(slides),
            "brand": presentation.title,
        },
    )


def _safe_redirect(request: HttpRequest, fallback_url: str):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect(fallback_url)


@login_required
def slide_list(request: HttpRequest, presentation_pk) -> HttpResponse:
    presentation_service.get_presentation(
        presentation_pk, requesting_user_id=request.user.id
    )
    result = slide_service.list_slides(presentation_pk)
    return render(
        request,
        "presentations/slide_list.html",
        {"slides": result.data, "presentation_pk": presentation_pk},
    )


@login_required
def slide_create(request: HttpRequest, presentation_pk) -> HttpResponse:
    if request.method == "POST":
        form = SlideForm(request.POST)
        if form.is_valid():
            slide_type = form.cleaned_data.get("slide_type") or "split"
            dto = CreateSlideDTO(
                presentation_id=presentation_pk,
                heading=form.cleaned_data.get("heading") or "Yeni Slayt",
                notes=form.cleaned_data.get("notes", ""),
                slide_type=slide_type,
                content=_starter_content(slide_type),
                position=-1,
            )
            slide_service.create_slide(dto, requesting_user_id=request.user.id)
            messages.success(request, "Slayt oluşturuldu.")
            return _safe_redirect(request, f"/presentations/{presentation_pk}/")
    else:
        form = SlideForm()

    return render(
        request,
        "presentations/slide_form.html",
        {"form": form, "presentation_pk": presentation_pk},
    )


@login_required
def slide_edit(request: HttpRequest, presentation_pk, pk) -> HttpResponse:
    slide_result = slide_service.get_slide(pk, requesting_user_id=request.user.id)
    slide = slide_result.data

    if request.method == "POST":
        form = SlideForm(request.POST)
        if form.is_valid():
            dto = UpdateSlideDTO(
                heading=form.cleaned_data.get("heading"),
                notes=form.cleaned_data.get("notes"),
                slide_type=form.cleaned_data.get("slide_type"),
            )
            slide_service.update_slide(pk, dto, requesting_user_id=request.user.id)
            messages.success(request, "Slayt güncellendi.")
            return _safe_redirect(request, f"/presentations/{presentation_pk}/")
    else:
        form = SlideForm(initial={
            "heading": slide.heading,
            "notes": slide.notes,
            "slide_type": slide.slide_type,
        })

    return render(
        request,
        "presentations/slide_form.html",
        {"form": form, "presentation_pk": presentation_pk},
    )


@login_required
def slide_delete(request: HttpRequest, presentation_pk, pk) -> HttpResponse:
    if request.method == "POST":
        slide_service.delete_slide(pk, requesting_user_id=request.user.id)
        messages.success(request, "Slayt silindi.")
    return _safe_redirect(request, f"/presentations/{presentation_pk}/")


@login_required
def slide_update(request: HttpRequest, presentation_pk, pk) -> HttpResponse:
    """AJAX: save a slide's structured content and return the re-rendered card."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    dto = UpdateSlideDTO(
        heading=data.get("heading"),
        slide_type=data.get("slide_type"),
        content=data.get("content"),
    )
    slide_service.update_slide(pk, dto, requesting_user_id=request.user.id)

    pres_result = presentation_service.get_presentation(
        presentation_pk, requesting_user_id=request.user.id
    )
    presentation = pres_result.data
    slide = next((s for s in presentation.slides.all() if str(s.pk) == str(pk)), None)
    if slide is None:
        return JsonResponse({"error": "not found"}, status=404)

    return JsonResponse(
        {"html": _render_slide_fragment(presentation, slide), "heading": slide.heading}
    )


@login_required
def slide_ai_edit(request: HttpRequest, presentation_pk, pk) -> HttpResponse:
    """AJAX: apply a natural-language instruction to a slide via the AI assistant."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    instruction = (data.get("instruction") or "").strip()
    if not instruction:
        return JsonResponse({"message": "Lütfen bir komut yazın."}, status=400)

    raw_history = data.get("history") or []
    history = tuple(
        (str(m.get("role", "")), str(m.get("text", "")))
        for m in raw_history
        if isinstance(m, dict) and m.get("role") in ("user", "assistant")
    )[-8:]

    slide_result = slide_service.get_slide(pk, requesting_user_id=request.user.id)
    slide = slide_result.data

    pres_result = presentation_service.get_presentation(
        presentation_pk, requesting_user_id=request.user.id
    )
    presentation = pres_result.data
    all_slides = list(presentation.slides.all())
    outline = tuple(
        f"{i + 1}. {s.heading}" + (" (şu an düzenlenen slayt)" if str(s.pk) == str(pk) else "")
        for i, s in enumerate(all_slides)
    )

    edit_result = edit_slide_with_instruction(
        slide_type=slide.slide_type,
        heading=slide.heading,
        content=slide.content,
        instruction=instruction,
        presentation_title=presentation.title,
        outline=outline,
        history=history,
    )
    if not edit_result.success:
        return JsonResponse(
            {"message": "Bu isteği uygulayamadım, farklı bir şekilde dener misin?"},
            status=200,
        )

    edited = edit_result.data.slide
    slide_service.update_slide(
        pk,
        UpdateSlideDTO(
            heading=edited.heading,
            slide_type=edited.slide_type,
            content=edited.content,
        ),
        requesting_user_id=request.user.id,
    )

    pres_result = presentation_service.get_presentation(
        presentation_pk, requesting_user_id=request.user.id
    )
    presentation = pres_result.data
    fresh = next((s for s in presentation.slides.all() if str(s.pk) == str(pk)), None)

    return JsonResponse({
        "message": edit_result.data.message or "Slaytı güncelledim.",
        "html": _render_slide_fragment(presentation, fresh) if fresh else "",
        "heading": edited.heading,
        "slide_type": edited.slide_type,
        "content": edited.content,
    })


@login_required
def slide_reorder(request: HttpRequest, presentation_pk) -> HttpResponse:
    if request.method == "POST":
        data = json.loads(request.body)
        slide_ids = data.get("slide_ids", [])
        slide_service.reorder_slides(
            presentation_pk, slide_ids, requesting_user_id=request.user.id
        )
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "POST required"}, status=405)


@login_required
def slide_regenerate(request: HttpRequest, presentation_pk, pk) -> HttpResponse:
    if request.method == "POST":
        pres_result = presentation_service.get_presentation(
            presentation_pk, requesting_user_id=request.user.id
        )
        presentation = pres_result.data
        slides = list(presentation.slides.all().order_by("position"))

        current_slide = None
        context_parts = []
        for s in slides:
            if str(s.pk) == str(pk):
                current_slide = s
            else:
                context_parts.append(f"- {s.heading}")

        if current_slide is None:
            messages.error(request, "Slayt bulunamadı.")
            return _safe_redirect(request, f"/presentations/{presentation_pk}/")

        result = regenerate_single_slide(
            topic=presentation.title,
            slide_context="\n".join(context_parts),
        )

        if result.success:
            slide_service.update_slide(
                pk,
                UpdateSlideDTO(
                    heading=result.data.heading,
                    notes=result.data.notes,
                    slide_type=result.data.slide_type,
                    content=result.data.content,
                ),
                requesting_user_id=request.user.id,
            )
            messages.success(request, "Slayt yeniden oluşturuldu.")
        else:
            messages.error(request, "Slayt yeniden oluşturulamadı.")

    return _safe_redirect(request, f"/presentations/{presentation_pk}/")
