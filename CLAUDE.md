# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

SlideAI — an AI-powered slide/presentation generation web application built with Django and MySQL, using server-side rendered templates with Bootstrap.

## Commands

```bash
# Setup
pip install -r requirements.txt
python manage.py migrate

# Run (dev)
python manage.py runserver

# Tests
python manage.py test

# Create superuser
python manage.py createsuperuser
```

Environment: copy `.env.sample` to `.env` and fill in required keys (SECRET_KEY, DB credentials, API keys).

## Architecture

### Project Layout
```
slideai/          — Django project settings (settings.py, urls.py, wsgi.py)
core/             — Main application (models, views, urls, forms)
templates/        — Django HTML templates (Bootstrap-based)
static/           — CSS, JS, images
```

### Tech Stack
- **Backend:** Python / Django
- **Database:** MySQL (via mysqlclient or PyMySQL)
- **Frontend:** Django templates + HTML/CSS/JavaScript + Bootstrap
- **AI Integration:** TBD (slide generation logic)

### Patterns
- Django MTV (Model-Template-View) architecture
- Server-side rendering with Django template engine
- Bootstrap for responsive UI components
- Static files served via Django's staticfiles app

## Conventions

### Python
- Follow Django conventions: fat models, thin views
- Use Django ORM for all database operations
- Class-based views preferred for CRUD, function-based for simple endpoints
- App-specific templates in `templates/{app_name}/`
- URL routing: project-level `slideai/urls.py` includes app-level `core/urls.py`

### Frontend
- Bootstrap 5 for layout and components
- Custom CSS in `static/css/`
- Custom JS in `static/js/`
- Static images in `static/images/`
- Base template with block inheritance (`base.html` → page templates)
- All pages extend `templates/base.html`

### Database
- MySQL as primary database
- Django migrations for schema management
- `python manage.py makemigrations` then `python manage.py migrate`
- Never edit migration files manually

### Testing
- Django's built-in TestCase for unit tests
- Tests live in each app's `tests.py` or `tests/` directory
- Run specific app tests: `python manage.py test core`

### Git
- `.idea/`, `__pycache__/`, `*.pyc`, `db.sqlite3`, `.env` should be in `.gitignore`
- Never commit secret keys or credentials
