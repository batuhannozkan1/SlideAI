# New Feature: $ARGUMENTS

Analyze the feature request and plan implementation following SlideAI's Service-Repository architecture.

## Step 1: Feature Analysis

Determine:
- Which app does this belong to? (accounts, presentations, core, or new app)
- Which layers need changes? (model, repository, service, view, form, template, URL)
- Are there existing patterns in the codebase similar to this feature?
- Does this touch the AI pipeline or export system?

Read existing code in the target app to understand current structure before proposing changes.

## Step 2: Implementation Plan

Present a bottom-up plan listing each file to create or modify:

```
1. Model:      apps/{app}/models/{name}.py (if new entity)
2. Migration:  python manage.py makemigrations
3. Repository: apps/{app}/repositories/{name}_repository.py (if new queries)
4. DTO:        apps/{app}/dtos.py (if new data transfer needed)
5. Service:    apps/{app}/services/{name}_service.py (business logic)
6. Form:       apps/{app}/forms/{name}_forms.py (if user input)
7. View:       apps/{app}/views/{name}_views.py (thin HTTP handler)
8. URL:        apps/{app}/urls.py (route registration)
9. Template:   templates/{app}/{name}.html (extends layouts/app.html)
```

Only include layers that actually need changes. Don't create files for layers that aren't needed.

## Step 3: Confirm & Execute

Wait for user approval before writing code. Then implement layer by layer, bottom-up.

## Rules

- Follow import rules strictly (views → services/forms only, services → repos only)
- Services are module-level functions, not classes
- DTOs are `@dataclass(frozen=True)`
- Views are thin `@login_required` FBVs
- Forms subclass `forms.Form`, never `ModelForm`
- Templates use Tailwind CSS, extend `layouts/app.html`
- No premature abstractions — 2+ usage rule for components
- Type hints on all function signatures
