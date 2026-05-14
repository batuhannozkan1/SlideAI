from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.presentations.services import export_service


@login_required
def export_pptx(request: HttpRequest, pk) -> HttpResponse:
    result = export_service.export_presentation(pk, "pptx", user_id=request.user.id)
    export_data = result.data
    response = HttpResponse(export_data.content, content_type=export_data.content_type)
    response["Content-Disposition"] = f'attachment; filename="{export_data.filename}"'
    return response


@login_required
def export_pdf(request: HttpRequest, pk) -> HttpResponse:
    return render(
        request,
        "errors/500.html",
        {"message": "PDF dışa aktarma yakında eklenecek."},
        status=501,
    )
