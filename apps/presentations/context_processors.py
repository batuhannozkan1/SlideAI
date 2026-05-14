from django.http import HttpRequest


def sidebar_context(request: HttpRequest) -> dict:
    if not request.user.is_authenticated:
        return {}

    from apps.presentations.services import presentation_service

    recent = presentation_service.get_recent_presentations(request.user.id, limit=5)
    total_presentations = presentation_service.get_total_presentation_count(request.user.id)
    total_slides = sum(p.slide_count for p in recent)

    return {
        "sidebar_recent_presentations": recent,
        "sidebar_total_presentations": total_presentations,
        "sidebar_total_slides": total_slides,
    }
