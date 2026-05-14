from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse

from apps.presentations.services import export_service


@login_required
def export_pdf(request: HttpRequest, pk) -> HttpResponse:
    result = export_service.export_presentation(pk, format="pdf")
    return JsonResponse({"status": "not_implemented", "format": "pdf"}, status=501)


@login_required
def export_pptx(request: HttpRequest, pk) -> HttpResponse:
    result = export_service.export_presentation(pk, format="pptx")
    return JsonResponse({"status": "not_implemented", "format": "pptx"}, status=501)
