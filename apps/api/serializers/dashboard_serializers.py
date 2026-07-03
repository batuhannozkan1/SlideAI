from __future__ import annotations

from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    """Flattens the frozen ``DashboardStatsDTO``."""

    total_presentations = serializers.IntegerField(read_only=True)
    total_slides = serializers.IntegerField(read_only=True)
    presentations_this_month = serializers.IntegerField(read_only=True)
    growth_percentage = serializers.FloatField(read_only=True)
    draft_count = serializers.IntegerField(read_only=True)
    published_count = serializers.IntegerField(read_only=True)
    chart_labels = serializers.ListField(child=serializers.CharField(), read_only=True)
    chart_values = serializers.ListField(child=serializers.IntegerField(), read_only=True)
    chart_max = serializers.IntegerField(read_only=True)
