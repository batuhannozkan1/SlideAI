Run a full architecture compliance check on the SlideAI codebase.

Scan all files under `apps/` for violations of the Service-Repository layer rules:

## Critical Checks (import rule violations)
1. **Views importing models/repos**: grep `from apps.*.models import` and `from apps.*.repositories import` in `apps/*/views/`
2. **Services calling .objects**: grep `.objects.` in `apps/*/services/`
3. **Services importing HTTP**: grep `from django.http` and `from django.shortcuts` in `apps/*/services/`
4. **Repos importing services/views**: grep `from apps.*.services import` and `from apps.*.views import` in `apps/*/repositories/`

## Pattern Checks (warnings)
5. **Class-based services**: grep `class.*Service` in `apps/*/services/`
6. **ModelForm usage**: grep `ModelForm` in `apps/*/forms/`
7. **Mutable DTOs**: check `dtos.py` files for `@dataclass` without `frozen=True`
8. **Logic in models**: check `apps/*/models/` for methods beyond `__str__`

## Convention Checks (info)
9. **Missing type hints**: sample view and service functions for return type annotations
10. **URL naming**: check `urls.py` files for underscore names (should be hyphens)

Report every finding with file path, line number, and fix suggestion. Group by severity.

If $ARGUMENTS is specified, only check that specific app (e.g., "presentations", "accounts").
