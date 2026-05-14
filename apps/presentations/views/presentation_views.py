from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.ai.dtos import GenerationRequest
from apps.ai.services.generation_service import generate_presentation_slides
from apps.presentations.dtos import CreatePresentationDTO, CreateSlideDTO, UpdatePresentationDTO
from apps.presentations.forms.ai_forms import AIGenerateForm
from apps.presentations.forms.presentation_forms import (
    PresentationCreateForm,
    PresentationEditForm,
)
from apps.presentations.services import presentation_service, slide_service
from apps.presentations.services import theme_service


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    stats = presentation_service.get_dashboard_stats(owner_id=request.user.id)
    recent = presentation_service.get_recent_presentations(owner_id=request.user.id, limit=5)
    return render(request, "presentations/dashboard.html", {
        "stats": stats,
        "recent_presentations": recent,
        "topbar_show_tabs": True,
    })


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
            theme = form.cleaned_data.get("theme")
            dto = CreatePresentationDTO(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                owner_id=request.user.id,
                theme_id=theme.pk if theme else None,
            )
            result = presentation_service.create_presentation(dto)
            messages.success(request, "Sunum oluşturuldu.")
            return redirect("presentations:detail", pk=result.data.pk)
    else:
        form = PresentationCreateForm()

    return render(request, "presentations/create.html", {"form": form})


@login_required
def presentation_detail(request: HttpRequest, pk) -> HttpResponse:
    result = presentation_service.get_presentation(
        pk, requesting_user_id=request.user.id
    )
    themes_result = theme_service.list_active_themes()
    return render(request, "presentations/detail.html", {
        "presentation": result.data,
        "themes": themes_result.data,
    })


@login_required
def presentation_edit(request: HttpRequest, pk) -> HttpResponse:
    current = presentation_service.get_presentation(
        pk, requesting_user_id=request.user.id
    )
    presentation = current.data

    if request.method == "POST":
        form = PresentationEditForm(request.POST)
        if form.is_valid():
            theme = form.cleaned_data.get("theme")
            dto = UpdatePresentationDTO(
                title=form.cleaned_data.get("title"),
                description=form.cleaned_data.get("description"),
                is_public=form.cleaned_data.get("is_public"),
                theme_id=theme.pk if theme else None,
            )
            presentation_service.update_presentation(
                pk, dto, requesting_user_id=request.user.id
            )
            messages.success(request, "Sunum güncellendi.")
            return redirect("presentations:detail", pk=pk)
    else:
        form = PresentationEditForm(
            initial={
                "title": presentation.title,
                "description": presentation.description,
                "is_public": presentation.is_public,
                "theme": presentation.theme_id,
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


@login_required
def presentation_generate(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AIGenerateForm(request.POST)
        if form.is_valid():
            template = form.cleaned_data.get("template")
            template_structure = template.structure if template else None

            gen_request = GenerationRequest(
                topic=form.cleaned_data["topic"],
                num_slides=form.cleaned_data["num_slides"],
                style=form.cleaned_data["style"],
                template_structure=template_structure,
                additional_instructions=form.cleaned_data.get("additional_instructions", ""),
            )

            result = generate_presentation_slides(gen_request)
            if not result.success:
                for error_list in result.errors.values():
                    for error in error_list:
                        messages.error(request, error)
                return render(request, "presentations/generate.html", {"form": form})

            gen_result = result.data
            theme = form.cleaned_data.get("theme")

            pres_dto = CreatePresentationDTO(
                title=gen_result.title_suggestion or form.cleaned_data["topic"],
                description=f"AI tarafından oluşturuldu: {form.cleaned_data['topic']}",
                owner_id=request.user.id,
                theme_id=theme.pk if theme else None,
            )
            pres_result = presentation_service.create_presentation(pres_dto)
            presentation = pres_result.data

            for i, slide_content in enumerate(gen_result.slides):
                slide_service.create_slide(
                    CreateSlideDTO(
                        presentation_id=presentation.pk,
                        heading=slide_content.heading,
                        body=slide_content.body,
                        notes=slide_content.notes,
                        layout=slide_content.layout,
                        position=i,
                    ),
                    requesting_user_id=request.user.id,
                )

            messages.success(request, "Sunum başarıyla oluşturuldu!")
            return redirect("presentations:detail", pk=presentation.pk)
    else:
        form = AIGenerateForm()

    return render(request, "presentations/generate.html", {"form": form})


@login_required
def presentation_present(request: HttpRequest, pk) -> HttpResponse:
    result = presentation_service.get_presentation(
        pk, requesting_user_id=request.user.id
    )
    return render(request, "presentations/present.html", {"presentation": result.data})


@login_required
def change_theme(request: HttpRequest, pk) -> HttpResponse:
    if request.method == "POST":
        theme_id = request.POST.get("theme_id") or None
        theme_service.apply_theme(pk, theme_id, user_id=request.user.id)
        messages.success(request, "Tema değiştirildi.")
    return redirect("presentations:detail", pk=pk)


@login_required
def presentation_duplicate(request: HttpRequest, pk) -> HttpResponse:
    if request.method == "POST":
        result = presentation_service.duplicate_presentation(
            pk, requesting_user_id=request.user.id
        )
        messages.success(request, "Sunum kopyalandı.")
        return redirect("presentations:detail", pk=result.data.pk)
    return redirect("presentations:detail", pk=pk)
