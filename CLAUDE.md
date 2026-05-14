# CLAUDE.md

## Project Overview

SlideAI — AI-powered presentation generation. Django + MySQL, server-side rendered with Bootstrap 5. Together AI (OpenAI-compat) for LLM, python-pptx for export.

## Commands

```bash
pip install -r requirements.txt       # Install deps
pip install -r requirements-dev.txt   # Dev deps (pytest, black, mypy)
python manage.py migrate              # Apply migrations
python manage.py seed_data            # Seed themes (6) + templates (4)
python manage.py runserver            # Dev server at :8000
python manage.py createsuperuser      # Admin user
pytest                                # Run tests
```

Environment: copy `.env.sample` → `.env`, fill in SECRET_KEY, DB credentials, AI config.

## Architecture — Service-Repository Pattern

```
HTTP Request → View (thin) → Service (pure logic) → Repository (ORM) → Model/DB
```

### Layer Rules
- **View** — parse HTTP, call service, return response. Never imports models or repositories.
- **Service** — pure business logic. Never touches request/response. Never calls .objects. Returns frozen DTOs.
- **Repository** — sole owner of ORM queries. Only layer that calls .objects.
- **Model** — pure data definition. Schema + `__str__` only. Zero logic.
- **DTO** — frozen dataclasses (`dtos.py`) for inter-layer data transfer.

### Import Rules (prevents circular imports)
```
models/       → only Django, stdlib
repositories/ → models/ only
services/     → repositories/ + core/dtos only
views/        → services/ + forms/ only
forms/        → models/ only (for ModelForm)
```

### Registry Patterns
- **AI Clients** — `apps/ai/clients/__init__.py`: `register_client(name, cls)` + `get_ai_client()`. Add provider = 1 file + self-register.
- **Exporters** — `apps/presentations/services/exporters/__init__.py`: `register_exporter(name, cls)` + `get_exporter()`. Add format = 1 file + self-register.

### Project Layout
```
config/              — Settings (base/dev/prod/test), urls, wsgi, asgi
apps/core/           — BaseRepository, exceptions, dtos, mixins, middleware, constants, views
apps/accounts/       — Auth (EmailAuthBackend), User model, profiles
apps/presentations/  — Presentations, slides, templates, themes, export
apps/ai/             — AI client registry, Together client, prompt system, generation pipeline
templates/           — 27 Django HTML templates (Bootstrap 5)
static/              — CSS (main, slides), JS (main, slideshow, reorder)
```

### Each App Internal Structure
```
app/
├── models/       — One file per model, __init__.py re-exports
├── repositories/ — One per model + singleton instances in __init__.py
├── services/     — Pure functions, frozen DTOs in/out (+ exporters/ subpackage)
├── views/        — Thin HTTP handlers
├── forms/        — Validation only
├── dtos.py       — App-specific frozen dataclasses
├── urls.py       — Namespaced URL patterns
└── tests/        — test_models, test_repositories, test_services, test_views
```

## Key Features & Flows

### AI Generation: View → Service → Client → API
```
presentation_generate view
  → AIGenerateForm.is_valid()
  → generation_service.generate_presentation_slides(GenerationRequest)
      → prompt_service.build_system_prompt() / build_user_prompt()
      → get_ai_client() → TogetherClient (from registry)
      → client.generate() → Together AI API (OpenAI-compat)
      → _validate_generation()
  → presentation_service.create_presentation()
  → slide_service.create_slide() × N
  → redirect → detail
```

### Export: View → Service → Exporter
```
export_pptx view → export_service.export_presentation(id, "pptx")
  → get_exporter("pptx") → PptxExporter (from registry)
  → exporter.export(presentation, slides, theme) → ExportResult
  → HttpResponse with .pptx attachment
```

### Theme System: CSS Custom Properties
Themes set `--slide-primary`, `--slide-secondary`, `--slide-accent`, `--slide-font-heading`, `--slide-font-body` via inline style. All visual rendering uses these vars. Zero Python needed for visual changes.

## Conventions

### Python
- Function-based views (thin). Services are module-level functions (not classes).
- Type hints everywhere. `frozen=True` dataclasses for DTOs. `tuple` for immutable collections.
- Custom exception hierarchy in `apps/core/exceptions.py` — middleware translates to HTTP.
- UUID primary keys via `UUIDPrimaryKeyMixin`. Soft delete via `SoftDeleteMixin`.

### Frontend
- Bootstrap 5 CDN. Base template with blocks (title, content, extra_css, extra_js).
- Components as partials: `_navbar.html`, `_footer.html`, `_messages.html`, `_pagination.html`, `_slide_card.html`.
- Slide preview: CSS custom properties + 16:9 aspect ratio cards.
- Fullscreen presentation: standalone HTML, keyboard/touch nav, progress bar.

### Database
- MySQL primary. Never edit migration files. Never bypass migrations.

### Testing
- Tests in `tests/` directory per app. Repos: integration (real DB). Services: unit (mock repos). Views: HTTP (Django client).
- `config/settings/test.py` with `AI_PROVIDER="mock"` for fast tests.

### Git
- `.idea/`, `__pycache__/`, `db.sqlite3`, `.env`, `staticfiles/`, `media/` in `.gitignore`
- Never commit secrets.
