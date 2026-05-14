from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.presentations.dtos import CreatePresentationDTO, UpdatePresentationDTO
from apps.presentations.forms.presentation_forms import (
    PresentationCreateForm,
    PresentationEditForm,
)
from apps.presentations.services import presentation_service


@login_required
def presentation_list(request: HttpRequest) -> HttpResponse:
    page = int(request.GET.get("page", 1))
    result = presentation_service.list_user_presentations(
        owner_id=request.user.id,
        page=page,
    )
    return render(request, "presentations/list.html", {"result": result})


@login_required
def presentation_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PresentationCreateForm(request.POST)
        if form.is_valid():
            dto = CreatePresentationDTO(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                owner_id=request.user.id,
                theme_id=form.cleaned_data.get("theme"),
            )
            result = presentation_service.create_presentation(dto)
            messages.success(request, "Presentation created.")
            return redirect("presentations:detail", pk=result.data.pk)
    else:
        form = PresentationCreateForm()

    return render(request, "presentations/create.html", {"form": form})


@login_required
def presentation_detail(request: HttpRequest, pk) -> HttpResponse:
    result = presentation_service.get_presentation(
        pk, requesting_user_id=request.user.id
    )
    return render(request, "presentations/detail.html", {"presentation": result.data})


@login_required
def presentation_edit(request: HttpRequest, pk) -> HttpResponse:
    current = presentation_service.get_presentation(
        pk, requesting_user_id=request.user.id
    )
    presentation = current.data

    if request.method == "POST":
        form = PresentationEditForm(request.POST)
        if form.is_valid():
            dto = UpdatePresentationDTO(
                title=form.cleaned_data.get("title"),
                description=form.cleaned_data.get("description"),
                is_public=form.cleaned_data.get("is_public"),
            )
            presentation_service.update_presentation(
                pk, dto, requesting_user_id=request.user.id
            )
            messages.success(request, "Presentation updated.")
            return redirect("presentations:detail", pk=pk)
    else:
        form = PresentationEditForm(
            initial={
                "title": presentation.title,
                "description": presentation.description,
                "is_public": presentation.is_public,
            }
        )

    return render(
        request,
        "presentations/edit.html",
        {"form": form, "presentation": presentation},
    )


@login_required
def presentation_delete(request: HttpRequest, pk) -> HttpResponse:
    if request.method == "POST":
        presentation_service.delete_presentation(
            pk, requesting_user_id=request.user.id
        )
        messages.success(request, "Presentation deleted.")
        return redirect("presentations:list")

    result = presentation_service.get_presentation(
        pk, requesting_user_id=request.user.id
    )
    return render(
        request, "presentations/confirm_delete.html", {"presentation": result.data}
    )
