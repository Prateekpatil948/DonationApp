# Analyst Platform Backend API

Production-grade Django REST Framework backend for the Analyst Platform Android application. Google OAuth login, JWT authentication (access + refresh), role-based permissions (Analyst / Subscriber), structured JSON logging, and Swagger/OpenAPI documentation for every endpoint.

## Tech Stack

- Python 3.12, Django 5.x, Django REST Framework
- PostgreSQL 16 (UUID primary keys everywhere)
- Redis (cache + throttling)
- SimpleJWT (access/refresh tokens with rotation + blacklisting)
- drf-spectacular (Swagger/ReDoc)
- Docker, Docker Compose, Gunicorn, Nginx-ready

## Architecture

```
Android App -> REST APIs -> Views (authenticate/validate/invoke/respond)
                          -> Services (business logic)
                          -> ORM / Models -> PostgreSQL
```

Views never touch the ORM directly - see `services.base.BaseService` and each app's `services.py`.

## Folder Structure

```
config/            Django settings (base/dev/prod/test), root urls, wsgi/asgi
apps/
  common/          Abstract BaseModel (UUID pk, timestamps, soft delete)
  users/           Custom User model, profile APIs
  authentication/  Google OAuth + JWT login, logout, refresh
  analytics/       Reserved for analyst-facing reporting (future)
  subscribers/     Reserved for subscriber-specific domain logic (future)
  notifications/   NotificationService seam for push/email/SMS (future)
core/
  exceptions/      ApplicationError hierarchy + global DRF exception handler
  middleware/      Request ID, response time, request logging, security headers
  permissions/     Role-based DRF permission classes (Analyst/Subscriber/Admin)
  pagination/      Standard page-number pagination (20/page, max 100)
  logging/         JSON log formatter
  validators/      Shared field validators (phone number)
  constants/       Shared enums (UserType, ErrorCode)
services/          Cross-app service base class
utils/             Response envelope helpers (success_response/error_response)
tests/             Project-wide test scaffolding
docker/            Dockerfile, nginx config
scripts/           Entrypoint + wait-for-db scripts
```

## Setup

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (recommended)
- PostgreSQL 16+ and Redis if running natively

### Environment variables

Copy `.env.example` to `.env` and fill in real values (Google OAuth credentials, `SECRET_KEY`, `JWT_SECRET`, etc.). Never commit `.env`.

```bash
cp .env.example .env
```

### Local development (Docker, recommended)

```bash
docker compose up --build
```

This starts `backend` (Django dev server on `:8000`), `db` (Postgres), and `redis`. Migrations run automatically via `scripts/entrypoint.sh`. To also run Nginx in front of the backend:

```bash
docker compose --profile nginx up --build
```

### Local development (without Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt
export DJANGO_SETTINGS_MODULE=config.settings.dev
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Production

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Uses `config.settings.prod`, Gunicorn, and Nginx as a reverse proxy serving `/static` and `/media` directly.

## API Documentation

- Swagger UI: `GET /api/docs/`
- ReDoc: `GET /api/redoc/`
- Raw OpenAPI schema: `GET /api/schema/`

## Core Endpoints

| Method | Path                          | Description                       |
|--------|-------------------------------|------------------------------------|
| POST   | `/api/v1/auth/google/login`   | Verify Google ID token, login/signup, issue JWT pair |
| POST   | `/api/v1/auth/logout`         | Blacklist a refresh token          |
| POST   | `/api/v1/auth/refresh`        | Exchange refresh token for new access token |
| GET    | `/api/v1/users/me`            | Fetch current user profile         |
| PUT    | `/api/v1/users/me`            | Update editable profile fields     |
| GET    | `/health`                     | Liveness/readiness probe (db, cache, version, uptime) |

All responses use a uniform envelope:

```json
{"success": true, "message": "Login successful", "data": {}}
```

```json
{"success": false, "error": {"code": "INVALID_TOKEN", "message": "Google token invalid"}}
```

## Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

Every model change must ship a migration with a meaningful name (`--name`); never hand-write SQL.

## Testing

```bash
pytest                          # runs the full suite with coverage
coverage report --fail-under=90 # enforce the 90% minimum gate
```

Tests live alongside each app in `apps/<app>/tests/` (`test_models.py`, `test_serializers.py`, `test_services.py`, `test_views.py`) plus `core/tests/` for cross-cutting concerns (exception handler, health check). Fixtures and factories: `conftest.py` (root) and `apps/users/tests/factories.py` (factory-boy).

## Coding Guidelines

- `black` (line length 100), `isort` (black profile), `flake8`, `mypy` (django-stubs/drf-stubs)
- Explicit serializer fields only - never `fields = "__all__"`
- Business logic lives in `services.py`; views only authenticate, validate, invoke, respond
- Max function size 50 lines, max class size 300 lines

Run all checks locally before pushing:

```bash
black . && isort . && flake8 . && mypy apps core services utils config
```

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`): lint -> test + coverage gate -> Docker build, on every push/PR to `main`.

## Troubleshooting

- **`django.db.utils.OperationalError` on startup**: Postgres isn't ready yet - `scripts/wait_for_db.sh` handles this in Docker; natively, confirm `DATABASE_URL` and that Postgres is running.
- **Google login returns `INVALID_TOKEN`**: confirm `GOOGLE_CLIENT_ID` matches the Android app's OAuth client, and that the ID token audience matches.
- **401 on every authenticated request**: check `Authorization: Bearer <access_token>` header and that `JWT_SECRET`/`SIMPLE_JWT` settings match between token issuance and verification.
- **Coverage gate fails in CI**: run `pytest` locally and inspect `htmlcov/index.html` for uncovered lines.
