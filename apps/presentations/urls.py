from django.urls import path

from apps.presentations.views import (
    export_views,
    presentation_views,
    slide_views,
)

app_name = "presentations"

urlpatterns = [
    # Presentations CRUD
    path("", presentation_views.presentation_list, name="list"),
    path("create/", presentation_views.presentation_create, name="create"),
    path("generate/", presentation_views.presentation_generate, name="generate"),
    path("<uuid:pk>/", presentation_views.presentation_detail, name="detail"),
    path("<uuid:pk>/editor/", presentation_views.presentation_editor, name="editor"),
    path("<uuid:pk>/present/", presentation_views.presentation_present, name="present"),
    path("<uuid:pk>/theme/", presentation_views.change_theme, name="change-theme"),
    path("<uuid:pk>/duplicate/", presentation_views.presentation_duplicate, name="duplicate"),
    path("<uuid:pk>/delete/", presentation_views.presentation_delete, name="delete"),
    # Slides
    path("<uuid:presentation_pk>/slides/", slide_views.slide_list, name="slide-list"),
    path("<uuid:presentation_pk>/slides/create/", slide_views.slide_create, name="slide-create"),
    path("<uuid:presentation_pk>/slides/<uuid:pk>/", slide_views.slide_edit, name="slide-edit"),
    path("<uuid:presentation_pk>/slides/<uuid:pk>/delete/", slide_views.slide_delete, name="slide-delete"),
    path("<uuid:presentation_pk>/slides/<uuid:pk>/regenerate/", slide_views.slide_regenerate, name="slide-regenerate"),
    path("<uuid:presentation_pk>/slides/reorder/", slide_views.slide_reorder, name="slide-reorder"),
    # Export
    path("<uuid:pk>/export/pdf/", export_views.export_pdf, name="export-pdf"),
    path("<uuid:pk>/export/pptx/", export_views.export_pptx, name="export-pptx"),
]
