from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.accounts.forms.profile_forms import ProfileEditForm
from apps.accounts.services import profile_service


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    result = profile_service.get_profile(request.user.id)
    return render(request, "accounts/profile.html", {"profile": result.data})


@login_required
def profile_edit_view(request: HttpRequest) -> HttpResponse:
    result = profile_service.get_profile(request.user.id)
    profile = result.data

    if request.method == "POST":
        form = ProfileEditForm(request.POST)
        if form.is_valid():
            profile_service.update_profile(
                request.user.id,
                bio=form.cleaned_data.get("bio"),
                avatar_url=form.cleaned_data.get("avatar_url"),
            )
            messages.success(request, "Profile updated.")
            return render(request, "accounts/profile.html", {"profile": profile})
    else:
        form = ProfileEditForm(initial={"bio": profile.bio, "avatar_url": profile.avatar_url})

    return render(request, "accounts/profile_edit.html", {"form": form})
