import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from apps.ai.services.generation_service import regenerate_single_slide
from apps.presentations.dtos import CreateSlideDTO, UpdateSlideDTO
from apps.presentations.forms.slide_forms import SlideForm
from apps.presentations.services import presentation_service, slide_service


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
            dto = CreateSlideDTO(
                presentation_id=presentation_pk,
                heading=form.cleaned_data["heading"],
                body=form.cleaned_data["body"],
                notes=form.cleaned_data.get("notes", ""),
                layout=form.cleaned_data.get("layout", "content"),
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
                body=form.cleaned_data.get("body"),
                notes=form.cleaned_data.get("notes"),
                layout=form.cleaned_data.get("layout"),
            )
            slide_service.update_slide(pk, dto, requesting_user_id=request.user.id)
            messages.success(request, "Slayt güncellendi.")
            return _safe_redirect(request, f"/presentations/{presentation_pk}/")
    else:
        form = SlideForm(initial={
            "heading": slide.heading,
            "body": slide.body,
            "notes": slide.notes,
            "layout": slide.layout,
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
                    body=result.data.body,
                    notes=result.data.notes,
                    layout=result.data.layout,
                ),
                requesting_user_id=request.user.id,
            )
            messages.success(request, "Slayt yeniden oluşturuldu.")
        else:
            messages.error(request, "Slayt yeniden oluşturulamadı.")

    return _safe_redirect(request, f"/presentations/{presentation_pk}/")
