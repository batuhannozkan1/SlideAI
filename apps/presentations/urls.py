from django.urls import path

from apps.presentations.views import (
    export_views,
    presentation_views,
    slide_views,
    template_views,
)

app_name = "presentations"

urlpatterns = [
    # Presentations CRUD
    path("", presentation_views.presentation_list, name="list"),
    path("create/", presentation_views.presentation_create, name="create"),
    path("<uuid:pk>/", presentation_views.presentation_detail, name="detail"),
    path("<uuid:pk>/edit/", presentation_views.presentation_edit, name="edit"),
    path("<uuid:pk>/delete/", presentation_views.presentation_delete, name="delete"),
    # Slides
    path("<uuid:presentation_pk>/slides/", slide_views.slide_list, name="slide-list"),
    path("<uuid:presentation_pk>/slides/create/", slide_views.slide_create, name="slide-create"),
    path("<uuid:presentation_pk>/slides/<uuid:pk>/", slide_views.slide_edit, name="slide-edit"),
    path("<uuid:presentation_pk>/slides/<uuid:pk>/delete/", slide_views.slide_delete, name="slide-delete"),
    path("<uuid:presentation_pk>/slides/reorder/", slide_views.slide_reorder, name="slide-reorder"),
    # Templates
    path("templates/", template_views.template_gallery, name="template-gallery"),
    path("templates/<uuid:pk>/preview/", template_views.template_preview, name="template-preview"),
    # Export
    path("<uuid:pk>/export/pdf/", export_views.export_pdf, name="export-pdf"),
    path("<uuid:pk>/export/pptx/", export_views.export_pptx, name="export-pptx"),
]
