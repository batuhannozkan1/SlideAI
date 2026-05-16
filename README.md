# SlideAI

AI-powered presentation generation. Enter a topic, get professional slides — with themes, visual preview, fullscreen presentation mode, and PowerPoint export.

## Tech Stack

- **Backend:** Python 3.12 / Django 5.1
- **Database:** MySQL
- **Frontend:** Django Templates + Tailwind CSS
- **AI:** Together AI (OpenAI-compatible API, Llama 3.3 70B)
- **Export:** python-pptx (PowerPoint)

## Quick Start

```bash
# Clone & enter
git clone <repo-url>
cd SlideAI

# Virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Environment variables
cp .env.sample .env
# Edit .env with your credentials (see Configuration below)

# Database
python manage.py migrate

# Seed themes & templates
python manage.py seed_data

# Create admin user
python manage.py createsuperuser

# Run
python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000)

## Features

- **AI Slide Generation** — Enter a topic, pick a style and template, AI generates complete slide content
- **Template-Driven** — 4 built-in templates (Pitch Deck, Educational, Business Report, Project Proposal) guide AI output structure
- **6 Themes** — Corporate Blue, Dark Mode, Minimalist, Nature Green, Warm Sunset, Tech Neon
- **Visual Preview** — 16:9 slide cards with theme colors, drag-drop reorder
- **Presentation Mode** — Fullscreen slideshow with keyboard/touch navigation
- **Theme Switching** — One-click theme change on any presentation
- **PowerPoint Export** — Download .pptx with theme colors, fonts, and speaker notes
- **Slide Regeneration** — Regenerate individual slides with AI
- **Public Sharing** — Share link for public presentations
- **Duplicate** — Copy any presentation with all slides

## Architecture

SlideAI follows the **Service-Repository** pattern with **Registry Patterns** for extensibility:

```
HTTP Request
    → View        (parse request, call service, return response)
    → Service     (pure business logic, no HTTP, no ORM)
    → Repository  (all database queries live here)
    → Model       (data definition only)
```

### Extension Points

| Want to add... | How |
|----------------|-----|
| New AI provider | 1 file in `apps/ai/clients/`, call `register_client()` |
| New export format | 1 file in `apps/presentations/services/exporters/`, call `register_exporter()` |
| New slide template | Add via admin panel or `seed_data` command |
| New theme | Add via admin panel or `seed_data` command |
| New slide layout | Add to `SlideLayout` enum + CSS class + pptx mapping |

### Project Structure

```
config/                       Django settings (base/dev/prod/test)
apps/
├── core/                    Shared foundation
│   ├── base_repository.py   Generic BaseRepository[T]
│   ├── exceptions.py        Custom exception hierarchy
│   ├── dtos.py              ServiceResult, PaginatedResult
│   ├── mixins.py            UUID PK, timestamps, soft delete
│   ├── middleware/           DomainExceptionMiddleware
│   ├── constants.py         SlideLayout enum
│   └── views.py             Landing page
├── accounts/                Authentication
│   ├── models/              User, UserProfile
│   ├── backends.py          EmailAuthBackend
│   ├── services/            auth_service, profile_service
│   └── views/               register, login, logout, profile
├── presentations/           Main domain
│   ├── models/              Presentation, Slide, SlideTemplate, Theme
│   ├── repositories/        4 repositories + singletons
│   ├── services/
│   │   ├── presentation_service.py  CRUD + duplicate
│   │   ├── slide_service.py         CRUD + reorder
│   │   ├── theme_service.py         list, apply
│   │   ├── export_service.py        registry-based export
│   │   └── exporters/               BaseExporter + PptxExporter
│   ├── views/               presentations, slides, export, templates (template routes are top-level)
│   ├── forms/               PresentationForms, SlideForm, AIGenerateForm
│   ├── management/commands/ seed_data
│   └── urls.py              17 URL patterns
└── ai/                      AI integration
    ├── clients/             Registry + TogetherClient + BaseAIClient ABC
    ├── services/            generation_service, prompt_service
    ├── prompts/             System/user prompt templates
    ├── dtos.py              GenerationRequest, SlideContent, GenerationResult
    └── tests/               MockAIClient
templates/                   32 templates (Tailwind CSS)
static/
├── css/                     app.css, slides.css
└── js/                      app.js, slideshow.js, slide-reorder.js
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_ENV` | `development` / `production` / `test` | `development` |
| `SECRET_KEY` | Django secret key | — |
| `DB_NAME` | MySQL database name | `slideai` |
| `DB_USER` | MySQL user | `root` |
| `DB_PASSWORD` | MySQL password | — |
| `DB_HOST` | MySQL host | `127.0.0.1` |
| `DB_PORT` | MySQL port | `3306` |
| `AI_PROVIDER` | AI provider: `together` or `mock` | — |
| `AI_API_KEY` | Together AI API key | — |
| `AI_MODEL` | Model ID (e.g. `meta-llama/Llama-3.3-70B-Instruct-Turbo`) | — |
| `AI_BASE_URL` | API base URL (e.g. `https://api.together.xyz/v1`) | — |
| `AI_MAX_SLIDES` | Maximum slides per generation | `20` |
| `AI_DEFAULT_SLIDES` | Default slide count | `8` |

### Settings

Settings are split by environment:

- `config/settings/base.py` — Shared configuration
- `config/settings/development.py` — Debug mode, console email, SQLite fallback
- `config/settings/production.py` — Security headers, HTTPS enforcement
- `config/settings/test.py` — Fast password hasher, mock AI provider

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run specific app tests
pytest apps/accounts/
pytest apps/presentations/

# Code formatting
black .
isort .

# Type checking
mypy .

# Linting
flake8
```

### Seed Data

The `seed_data` management command creates:
- **6 themes** with colors and fonts
- **4 slide templates** with structured JSON layouts (Pitch Deck, Educational Lesson, Business Report, Project Proposal)

```bash
python manage.py seed_data
```

Idempotent — safe to run multiple times.

## API Routes

### Dashboard
- `GET /dashboard/` — User dashboard with stats and recent presentations

### Presentations (9 routes)
- `GET /presentations/` — List user's presentations
- `GET /presentations/create/` — Manual creation form
- `GET /presentations/generate/` — AI generation form
- `GET /presentations/<uuid>/` — Detail with visual slide grid
- `GET /presentations/<uuid>/present/` — Fullscreen presentation mode
- `POST /presentations/<uuid>/theme/` — Change theme
- `POST /presentations/<uuid>/duplicate/` — Duplicate presentation
- `GET /presentations/<uuid>/edit/` — Edit form
- `POST /presentations/<uuid>/delete/` — Delete presentation

### Slides (6 routes)
- `GET /presentations/<uuid>/slides/` — List slides
- `POST /presentations/<uuid>/slides/create/` — Add slide
- `POST /presentations/<uuid>/slides/<uuid>/edit/` — Edit slide
- `POST /presentations/<uuid>/slides/<uuid>/delete/` — Delete slide
- `POST /presentations/<uuid>/slides/<uuid>/regenerate/` — AI regenerate slide
- `POST /presentations/<uuid>/slides/reorder/` — Reorder (JSON)

### Templates (2 routes)
- `GET /templates/` — Template gallery
- `GET /templates/<uuid>/preview/` — Template preview

### Export (2 routes)
- `GET /presentations/<uuid>/export/pptx/` — Download PowerPoint
- `GET /presentations/<uuid>/export/pdf/` — PDF (coming soon)

## License

All rights reserved.
