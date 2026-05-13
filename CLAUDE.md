# CLAUDE.md

## Project Overview

SlideAI — AI-powered presentation generation. Django + MySQL, server-side rendered with Bootstrap 5.

## Commands

```bash
pip install -r requirements.txt    # Setup
python manage.py migrate           # Apply migrations
python manage.py runserver         # Dev server
python manage.py test              # Tests
python manage.py createsuperuser   # Admin user
```

Environment: copy `.env.sample` → `.env`, fill in SECRET_KEY, DB credentials, AI_PROVIDER.

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

### Project Layout
```
config/              — Django settings (base/dev/prod), urls, wsgi, asgi
apps/core/           — Shared: BaseRepository, exceptions, dtos, mixins, middleware
apps/accounts/       — Auth, User model, profiles
apps/presentations/  — Main domain: presentations, slides, templates, themes
apps/ai/             — AI integration (provider-agnostic, isolated)
templates/           — Django HTML templates (Bootstrap 5)
static/              — CSS, JS, images
```

### Each App Internal Structure
```
app/
├── models/       — One file per model, __init__.py re-exports
├── repositories/ — One per model + singleton instances in __init__.py
├── services/     — Pure functions, frozen DTOs in/out
├── views/        — Thin HTTP handlers
├── forms/        — Validation only
├── dtos.py       — App-specific frozen dataclasses
├── urls.py       — Namespaced URL patterns
└── tests/        — test_models, test_repositories, test_services, test_views
```

## Conventions

### Python
- Function-based views (thin). Services are module-level functions (not classes).
- Type hints everywhere. `frozen=True` dataclasses for DTOs. `tuple` for immutable collections.
- Custom exception hierarchy in `apps/core/exceptions.py` — middleware translates to HTTP.
- UUID primary keys via `UUIDPrimaryKeyMixin`. Soft delete via `SoftDeleteMixin`.

### Frontend
- Bootstrap 5 CDN. Base template with blocks (title, content, extra_css, extra_js).
- Components as partials: `_navbar.html`, `_footer.html`, `_messages.html`, `_pagination.html`.

### Database
- MySQL primary (SQLite fallback in dev when DB_NAME not set).
- Never edit migration files. Never bypass migrations.

### Testing
- Tests in `tests/` directory per app. Repos: integration (real DB). Services: unit (mock repos). Views: HTTP (Django client).

### Git
- `.idea/`, `__pycache__/`, `db.sqlite3`, `.env`, `staticfiles/`, `media/` in `.gitignore`
- Never commit secrets.
