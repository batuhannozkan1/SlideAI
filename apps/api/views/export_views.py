"""Export endpoint — streams the binary .pptx produced by the exporter registry."""
from __future__ import annotations

from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.presentations.services import export_service


class ExportPptxView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        result = export_service.export_presentation(
            pk, "pptx", user_id=request.user.id
        )
        export = result.data
        response = HttpResponse(export.content, content_type=export.content_type)
        response["Content-Disposition"] = f'attachment; filename="{export.filename}"'
        return response
