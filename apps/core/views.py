from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def landing_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "landing.html")
