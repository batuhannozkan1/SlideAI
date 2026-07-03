from django.core.management.base import BaseCommand

from apps.presentations.models import SlideTemplate, Theme


# Brand-driven themes (design-guide system). primary_color = brand color,
# accent_color = brand-dark (used for gradients / eyebrow-dark / stat values).
# secondary_color kept for the pptx exporter (text color on a solid brand bg).
THEMES = [
    {
        "name": "Teknoloji (Teal)",
        "primary_color": "#0d9488",
        "secondary_color": "#ffffff",
        "accent_color": "#115e59",
        "font_heading": "Inter",
        "font_body": "Inter",
    },
    {
        "name": "Akademik (Mavi)",
        "primary_color": "#2563eb",
        "secondary_color": "#ffffff",
        "accent_color": "#1e40af",
        "font_heading": "Inter",
        "font_body": "Inter",
    },
    {
        "name": "Sağlık (Yeşil)",
        "primary_color": "#16a34a",
        "secondary_color": "#ffffff",
        "accent_color": "#166534",
        "font_heading": "Inter",
        "font_body": "Inter",
    },
    {
        "name": "Finans (Lacivert)",
        "primary_color": "#1e3a8a",
        "secondary_color": "#ffffff",
        "accent_color": "#172554",
        "font_heading": "Inter",
        "font_body": "Inter",
    },
    {
        "name": "Enerji (Turuncu)",
        "primary_color": "#ea580c",
        "secondary_color": "#ffffff",
        "accent_color": "#9a3412",
        "font_heading": "Inter",
        "font_body": "Inter",
    },
    {
        "name": "Yaratıcı (Mor)",
        "primary_color": "#7c3aed",
        "secondary_color": "#ffffff",
        "accent_color": "#5b21b6",
        "font_heading": "Inter",
        "font_body": "Inter",
    },
]

# Template structures guide the AI. "type" maps to Slide.slide_type
# (cover / split / closing); "hint" describes the slide's content.
TEMPLATES = [
    {
        "name": "Pitch Deck",
        "description": "Startup veya proje sunumu için ideal yapı",
        "structure": {
            "slides": [
                {"role": "title", "type": "cover", "hint": "Company/project name and tagline"},
                {"role": "problem", "type": "split", "hint": "The problem being solved"},
                {"role": "solution", "type": "split", "hint": "Your unique solution"},
                {"role": "features", "type": "split", "hint": "Key features or benefits"},
                {"role": "market", "type": "split", "hint": "Market opportunity and size"},
                {"role": "business_model", "type": "split", "hint": "How you make money"},
                {"role": "traction", "type": "split", "hint": "Progress and milestones"},
                {"role": "team", "type": "split", "hint": "Core team members"},
                {"role": "roadmap", "type": "split", "hint": "Future plans and timeline"},
                {"role": "closing", "type": "closing", "hint": "Call to action and contact info"},
            ]
        },
    },
    {
        "name": "Educational Lesson",
        "description": "Ders veya eğitim sunumu yapısı",
        "structure": {
            "slides": [
                {"role": "title", "type": "cover", "hint": "Lesson title and learning objectives"},
                {"role": "overview", "type": "split", "hint": "What we'll cover today"},
                {"role": "concept_1", "type": "split", "hint": "First key concept explanation"},
                {"role": "concept_2", "type": "split", "hint": "Second key concept explanation"},
                {"role": "example", "type": "split", "hint": "Practical example or case study"},
                {"role": "practice", "type": "split", "hint": "Exercise or discussion question"},
                {"role": "summary", "type": "split", "hint": "Key takeaways recap"},
                {"role": "closing", "type": "closing", "hint": "Questions and further reading"},
            ]
        },
    },
    {
        "name": "Business Report",
        "description": "Iş raporu ve analiz sunumu",
        "structure": {
            "slides": [
                {"role": "title", "type": "cover", "hint": "Report title and date"},
                {"role": "executive_summary", "type": "split", "hint": "High-level overview and key findings"},
                {"role": "data_analysis", "type": "split", "hint": "Data and metrics breakdown"},
                {"role": "insights", "type": "split", "hint": "Key insights from the data"},
                {"role": "challenges", "type": "split", "hint": "Current challenges and risks"},
                {"role": "recommendations", "type": "split", "hint": "Recommended actions"},
                {"role": "timeline", "type": "split", "hint": "Implementation timeline"},
                {"role": "closing", "type": "closing", "hint": "Summary and next steps"},
            ]
        },
    },
    {
        "name": "Project Proposal",
        "description": "Proje teklifi sunumu",
        "structure": {
            "slides": [
                {"role": "title", "type": "cover", "hint": "Project name and subtitle"},
                {"role": "background", "type": "split", "hint": "Context and motivation"},
                {"role": "objectives", "type": "split", "hint": "Project goals and success criteria"},
                {"role": "approach", "type": "split", "hint": "Methodology and approach"},
                {"role": "deliverables", "type": "split", "hint": "Expected outcomes and deliverables"},
                {"role": "budget", "type": "split", "hint": "Budget and resource requirements"},
                {"role": "closing", "type": "closing", "hint": "Call to action"},
            ]
        },
    },
]


class Command(BaseCommand):
    help = "Seed themes and slide templates"

    def handle(self, *args, **options):
        for theme_data in THEMES:
            Theme.objects.update_or_create(
                name=theme_data["name"],
                defaults=theme_data,
            )

        for tmpl_data in TEMPLATES:
            SlideTemplate.objects.update_or_create(
                name=tmpl_data["name"],
                defaults=tmpl_data,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(THEMES)} themes, {len(TEMPLATES)} templates"
            )
        )
