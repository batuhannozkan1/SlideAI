from django.contrib import admin

from apps.presentations.models import Presentation, Slide, SlideTemplate, Theme


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "theme", "is_public", "slide_count", "created_at")
    list_filter = ("is_public", "is_deleted", "theme")
    search_fields = ("title",)
    raw_id_fields = ("owner",)


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ("heading", "presentation", "position", "slide_type")
    list_filter = ("slide_type",)
    raw_id_fields = ("presentation",)


@admin.register(SlideTemplate)
class SlideTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "primary_color", "secondary_color", "accent_color", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
