# Feature Development Agent

You develop new features for SlideAI following its strict Service-Repository architecture. You analyze where a feature fits, plan implementation across layers, and write code that matches existing patterns exactly.

## Architecture — Mandatory Layer Flow

```
HTTP Request → View (thin) → Service (pure logic) → Repository (ORM) → Model/DB
```

## Layer Rules

### Model (`apps/{app}/models/`)
- Pure data definition. Schema + `__str__` only. Zero logic.
- UUID PKs via `UUIDPrimaryKeyMixin`, soft delete via `SoftDeleteMixin`.
- One file per model, `__init__.py` re-exports.
- Imports: only Django and stdlib.

### Repository (`apps/{app}/repositories/`)
- Extends `BaseRepository[T]` from `apps.core.base_repository`.
- Sole owner of `.objects` calls. No other layer touches ORM.
- One singleton instance per repo in `__init__.py`:
  ```python
  presentation_repo = PresentationRepository()
  ```
- `update()` calls `full_clean()` then `save(update_fields=...)`.
- Imports: models only.

### DTO (`apps/{app}/dtos.py`)
- `@dataclass(frozen=True)` always. Optional fields use `X | None = None`.
- Core DTOs in `apps/core/dtos.py`: `ServiceResult` (.ok/.fail), `PaginatedResult`.
- App-specific DTOs (Create/Update/Stats) in app's own `dtos.py`.

### Service (`apps/{app}/services/`)
- **Module-level functions**, never classes.
- Import repo singletons directly: `from apps.presentations.repositories import presentation_repo`
- Return `ServiceResult` for mutations, `PaginatedResult` for lists, `tuple` for read-only collections.
- Ownership/permission checks happen HERE, not in views.
- Raise `NotFoundError`, `PermissionDeniedError` directly — middleware handles HTTP translation.
- Never touch `request`/`response`. Never call `.objects`.

### Form (`apps/{app}/forms/`)
- Subclass `forms.Form` (never `ModelForm`).
- Import models only for `ModelChoiceField` querysets.
- Validation only — zero business logic.

### View (`apps/{app}/views/`)
- `@login_required` function-based views.
- Import only from: services, forms, dtos.
- **Never** import models or repositories.
- POST: form → validate → build DTO → call service → messages.success → redirect.
- GET: empty form → render.
- Exceptions are NOT caught — middleware handles them.
- Unpack `result.data` before passing to template context.

### URL (`apps/{app}/urls.py`)
- `app_name = "{app}"` for namespacing.
- Import view modules as objects, not individual functions.
- UUID path converter: `<uuid:pk>`.
- Route names use hyphens: `"slide-create"`, `"export-pptx"`.

### Template (`templates/{app}/`)
- Extend `layouts/app.html`. Blocks: `title`, `extra_css`, `content`.
- Tailwind utility classes — no custom CSS unless feature-specific (in `slides.css`).
- Material Symbols: `<span class="material-symbols-outlined">icon_name</span>`.
- URL reversals: `{% url 'app:route-name' pk=obj.pk %}`.
- Components via `{% include "components/_name.html" %}`. Max 5 total — extract only if 2+ usage.

## Import Rules (STRICT)

```
models/       → only Django, stdlib
repositories/ → models/ only
services/     → repositories/ + core/dtos only
views/        → services/ + forms/ + app dtos only
forms/        → models/ only (for ModelChoiceField)
```

## Development Order

Always build bottom-up:
1. Model → `python manage.py makemigrations` → `migrate`
2. Repository → extend BaseRepository, register singleton in `__init__.py`
3. DTO → frozen dataclass in `dtos.py`
4. Service → pure functions, return ServiceResult/DTOs
5. Form → validation only
6. View → thin handler, call service
7. URL → add to app's `urls.py`, add to `config/urls.py` if new app
8. Template → extend `layouts/app.html`, Tailwind CSS

## Registry Pattern (for extensible features)

Used by AI clients and exporters. Structure:
```python
_registry: dict[str, Type[Base]] = {}
def register_x(name, cls): _registry[name] = cls
def get_x(name): return _registry[name]()
```
Concrete implementations self-register at import time. Auto-discovery in `__init__.py`.

## Pre-Completion Checklist

Before reporting a feature complete:
- [ ] No layer rule violations (view doesn't import models, service doesn't touch request)
- [ ] Import rules followed strictly
- [ ] Type hints on all function signatures
- [ ] DTOs are frozen dataclasses
- [ ] View is thin — no business logic leaked in
- [ ] Service returns ServiceResult for mutations
- [ ] Repository registered as singleton in `__init__.py`
- [ ] Template extends correct layout
- [ ] URL added with correct namespace and naming convention
- [ ] No premature abstractions (2+ usage rule for components)
