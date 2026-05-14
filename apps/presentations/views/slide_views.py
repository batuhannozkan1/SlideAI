import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from apps.presentations.dtos import CreateSlideDTO, UpdateSlideDTO
from apps.presentations.forms.slide_forms import SlideForm
from apps.presentations.services import presentation_service, slide_service


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
            messages.success(request, "Slide created.")
            return redirect("presentations:detail", pk=presentation_pk)
    else:
        form = SlideForm()

    return render(
        request,
        "presentations/slide_form.html",
        {"form": form, "presentation_pk": presentation_pk},
    )


@login_required
def slide_edit(request: HttpRequest, presentation_pk, pk) -> HttpResponse:
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
            messages.success(request, "Slide updated.")
            return redirect("presentations:detail", pk=presentation_pk)
    else:
        form = SlideForm()

    return render(
        request,
        "presentations/slide_form.html",
        {"form": form, "presentation_pk": presentation_pk},
    )


@login_required
def slide_delete(request: HttpRequest, presentation_pk, pk) -> HttpResponse:
    if request.method == "POST":
        slide_service.delete_slide(pk, requesting_user_id=request.user.id)
        messages.success(request, "Slide deleted.")
    return redirect("presentations:detail", pk=presentation_pk)


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
