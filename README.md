# SlideAI

AI-powered presentation generation web application. Create professional slide decks with artificial intelligence assistance.

## Tech Stack

- **Backend:** Python 3.12 / Django 5.1
- **Database:** MySQL (SQLite fallback for development)
- **Frontend:** Django Templates + Bootstrap 5
- **AI:** Provider-agnostic integration layer (plug any LLM)

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
# Edit .env with your SECRET_KEY and DB credentials

# Database
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run
python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000)

## Architecture

SlideAI follows the **Service-Repository** pattern — a layered architecture where each layer has a single responsibility:

```
HTTP Request
    → View        (parse request, call service, return response)
    → Service     (pure business logic, no HTTP, no ORM)
    → Repository  (all database queries live here)
    → Model       (data definition only)
```

### Project Structure

```
config/                  Django project settings (base/dev/prod split)
apps/
├── core/               Shared foundation (base classes, exceptions, DTOs, mixins)
├── accounts/           Authentication, users, profiles
├── presentations/      Presentations, slides, templates, themes
└── ai/                 AI integration (provider-agnostic)
templates/              HTML templates (Bootstrap 5)
static/                 CSS, JS, images
```

### App Internal Layout

Each app follows the same consistent structure:

```
app/
├── models/             One file per model
├── repositories/       Data access layer (ORM queries)
├── services/           Business logic (pure functions)
├── views/              HTTP handlers (thin)
├── forms/              Form validation
├── dtos.py             Frozen dataclasses for data transfer
├── urls.py             URL routing (namespaced)
└── tests/              Tests organized by layer
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_ENV` | Environment: `development` / `production` | `development` |
| `SECRET_KEY` | Django secret key | — |
| `DB_NAME` | MySQL database name | `slideai` |
| `DB_USER` | MySQL user | `root` |
| `DB_PASSWORD` | MySQL password | — |
| `DB_HOST` | MySQL host | `127.0.0.1` |
| `DB_PORT` | MySQL port | `3306` |
| `AI_PROVIDER` | AI provider identifier | — |
| `AI_API_KEY` | AI service API key | — |
| `AI_MODEL` | AI model name | — |

> **Note:** In development, if `DB_NAME` is not set, the app automatically falls back to SQLite.

### Settings

Settings are split by environment:

- `config/settings/base.py` — Shared configuration
- `config/settings/development.py` — Debug mode, console email, SQLite fallback
- `config/settings/production.py` — Security headers, HTTPS enforcement

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
python manage.py test

# Run specific app tests
python manage.py test apps.accounts
python manage.py test apps.presentations

# Code formatting
black .
isort .

# Type checking
mypy .

# Linting
flake8
```

## License

All rights reserved.
