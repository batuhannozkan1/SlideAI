from django.core.management.base import BaseCommand

from apps.presentations.models import SlideTemplate, Theme


THEMES = [
    {
        "name": "Corporate Blue",
        "primary_color": "#1a365d",
        "secondary_color": "#ffffff",
        "accent_color": "#3182ce",
        "font_heading": "Inter",
        "font_body": "Inter",
    },
    {
        "name": "Dark Mode",
        "primary_color": "#1a1a2e",
        "secondary_color": "#e0e0e0",
        "accent_color": "#e94560",
        "font_heading": "Space Grotesk",
        "font_body": "Inter",
    },
    {
        "name": "Minimalist",
        "primary_color": "#ffffff",
        "secondary_color": "#333333",
        "accent_color": "#667eea",
        "font_heading": "Helvetica",
        "font_body": "Georgia",
    },
    {
        "name": "Nature Green",
        "primary_color": "#1b4332",
        "secondary_color": "#f0fff4",
        "accent_color": "#38a169",
        "font_heading": "Merriweather",
        "font_body": "Source Sans Pro",
    },
    {
        "name": "Warm Sunset",
        "primary_color": "#7c2d12",
        "secondary_color": "#fff7ed",
        "accent_color": "#f97316",
        "font_heading": "Playfair Display",
        "font_body": "Lato",
    },
    {
        "name": "Tech Neon",
        "primary_color": "#0f172a",
        "secondary_color": "#e2e8f0",
        "accent_color": "#06b6d4",
        "font_heading": "JetBrains Mono",
        "font_body": "Inter",
    },
]

TEMPLATES = [
    {
        "name": "Pitch Deck",
        "description": "Startup veya proje sunumu için ideal yapı",
        "structure": {
            "slides": [
                {"role": "title", "layout": "title", "hint": "Company/project name and tagline"},
                {"role": "problem", "layout": "content", "hint": "The problem being solved"},
                {"role": "solution", "layout": "content", "hint": "Your unique solution"},
                {"role": "features", "layout": "two_column", "hint": "Key features or benefits"},
                {"role": "market", "layout": "content", "hint": "Market opportunity and size"},
                {"role": "business_model", "layout": "content", "hint": "How you make money"},
                {"role": "traction", "layout": "content", "hint": "Progress and milestones"},
                {"role": "team", "layout": "two_column", "hint": "Core team members"},
                {"role": "roadmap", "layout": "content", "hint": "Future plans and timeline"},
                {"role": "closing", "layout": "title", "hint": "Call to action and contact info"},
            ]
        },
    },
    {
        "name": "Educational Lesson",
        "description": "Ders veya eğitim sunumu yapısı",
        "structure": {
            "slides": [
                {"role": "title", "layout": "title", "hint": "Lesson title and learning objectives"},
                {"role": "overview", "layout": "content", "hint": "What we'll cover today"},
                {"role": "concept_1", "layout": "content", "hint": "First key concept explanation"},
                {"role": "concept_2", "layout": "content", "hint": "Second key concept explanation"},
                {"role": "example", "layout": "two_column", "hint": "Practical example or case study"},
                {"role": "practice", "layout": "content", "hint": "Exercise or discussion question"},
                {"role": "summary", "layout": "content", "hint": "Key takeaways recap"},
                {"role": "closing", "layout": "title", "hint": "Questions and further reading"},
            ]
        },
    },
    {
        "name": "Business Report",
        "description": "Iş raporu ve analiz sunumu",
        "structure": {
            "slides": [
                {"role": "title", "layout": "title", "hint": "Report title and date"},
                {"role": "executive_summary", "layout": "content", "hint": "High-level overview and key findings"},
                {"role": "data_analysis", "layout": "two_column", "hint": "Data and metrics breakdown"},
                {"role": "insights", "layout": "content", "hint": "Key insights from the data"},
                {"role": "challenges", "layout": "content", "hint": "Current challenges and risks"},
                {"role": "recommendations", "layout": "content", "hint": "Recommended actions"},
                {"role": "timeline", "layout": "content", "hint": "Implementation timeline"},
                {"role": "closing", "layout": "title", "hint": "Summary and next steps"},
            ]
        },
    },
    {
        "name": "Project Proposal",
        "description": "Proje teklifi sunumu",
        "structure": {
            "slides": [
                {"role": "title", "layout": "title", "hint": "Project name and subtitle"},
                {"role": "background", "layout": "content", "hint": "Context and motivation"},
                {"role": "objectives", "layout": "content", "hint": "Project goals and success criteria"},
                {"role": "approach", "layout": "two_column", "hint": "Methodology and approach"},
                {"role": "deliverables", "layout": "content", "hint": "Expected outcomes and deliverables"},
                {"role": "budget", "layout": "content", "hint": "Budget and resource requirements"},
                {"role": "closing", "layout": "title", "hint": "Call to action"},
            ]
        },
    },
]


class Command(BaseCommand):
    help = "Seed themes and slide templates"

    def handle(self, *args, **options):
        theme_count = 0
        for theme_data in THEMES:
            _, created = Theme.objects.get_or_create(
                name=theme_data["name"],
                defaults=theme_data,
            )
            if created:
                theme_count += 1

        template_count = 0
        for tmpl_data in TEMPLATES:
            _, created = SlideTemplate.objects.get_or_create(
                name=tmpl_data["name"],
                defaults=tmpl_data,
            )
            if created:
                template_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {theme_count} themes, {template_count} templates"
            )
        )
