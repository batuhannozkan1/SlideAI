"""Themes, templates, and dashboard stats — read-only adapters over services."""
from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.presentations.services import presentation_service, template_service, theme_service

from ..serializers import DashboardStatsSerializer, TemplateSerializer, ThemeSerializer


class ThemeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        themes = theme_service.list_active_themes().data
        return Response({"results": ThemeSerializer(themes, many=True).data})


class TemplateListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        templates = template_service.list_templates().data
        return Response({"results": TemplateSerializer(templates, many=True).data})


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = presentation_service.get_dashboard_stats(owner_id=request.user.id)
        return Response(DashboardStatsSerializer(stats).data)
