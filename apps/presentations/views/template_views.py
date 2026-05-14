from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.presentations.services import template_service


@login_required
def template_gallery(request: HttpRequest) -> HttpResponse:
    result = template_service.list_templates()
    return render(request, "presentations/template_gallery.html", {"templates": result.data})


@login_required
def template_preview(request: HttpRequest, pk) -> HttpResponse:
    result = template_service.get_template(pk)
    return render(request, "presentations/template_preview.html", {"template": result.data})
