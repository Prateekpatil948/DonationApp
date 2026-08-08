# Temple Donation Management System (TDMS) Backend API

Production-grade Django REST Framework backend for the TDMS Android application. Phone number + PIN authentication (invite-only signup), JWT authentication (access + refresh), role-based permissions (Admin / Member), donation entry with auto-numbered receipts, multi-language (English/Kannada/Marathi) PDF receipts, admin reports with CSV/Excel/PDF export, structured JSON logging, and Swagger/OpenAPI documentation for every endpoint.

## Tech Stack

- Python 3.11+/3.12, Django 5.x, Django REST Framework
- PostgreSQL 16 (UUID primary keys everywhere)
- SimpleJWT (access/refresh tokens with rotation + blacklisting)
- WeasyPrint (multi-language PDF receipts/reports), openpyxl (Excel export)
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
  common/          Abstract BaseModel, TempleSettings (singleton config), AuditLog
  users/           Custom User model (phone+PIN), Invitations, member management APIs
  authentication/  Signup (PIN set-up), login, logout, refresh, change-pin
  donations/       DonationCategory (with goals), Donation (auto receipt numbering)
  receipts/        ReceiptTemplate, multi-language PDF generation (WeasyPrint)
  reports/         Admin-facing aggregation reports + CSV/Excel/PDF export
  notifications/   NotificationService seam for push/email/SMS (future)
core/
  exceptions/      ApplicationError hierarchy + global DRF exception handler
  middleware/      Request ID, response time, request logging, security headers
  permissions/     Role-based DRF permission classes (IsAdminRole, IsActiveMember)
  pagination/      Standard page-number pagination (20/page, max 100)
  logging/         JSON log formatter
  validators/      Shared field validators (phone number)
  constants/       Shared enums (UserRole, MemberStatus, PaymentMode, ReceiptLanguage, ErrorCode)
services/          Cross-app service base class
utils/             Response envelope helpers (success_response/error_response)
tests/             Project-wide test scaffolding
docker/            Dockerfile, nginx config
scripts/           Entrypoint + wait-for-db scripts
```

See [HANDOVER.md](HANDOVER.md) for the full API reference (endpoints, payloads, error codes, enums) intended for the Android team.

## Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- PostgreSQL 16+ if running natively

### Environment variables

Copy `.env.example` to `.env` and fill in real values (`SECRET_KEY`, `JWT_SECRET`, etc.). Never commit `.env`.

```bash
cp .env.example .env
```

### Local development (Docker, recommended)

```bash
docker compose up --build
```

This starts `backend` (Django dev server on `:8000`) and `db` (Postgres). Migrations run automatically via `scripts/entrypoint.sh`. To also run Nginx in front of the backend:

```bash
docker compose --profile nginx up --build
```

### Local development (without Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt
export DJANGO_SETTINGS_MODULE=config.settings.dev
python manage.py migrate
DJANGO_SUPERUSER_PHONE_NUMBER=+919876500000 DJANGO_SUPERUSER_PIN=123456 python manage.py bootstrap_superuser
python manage.py runserver
```

WeasyPrint needs native libraries to render PDFs (`libpango`, `libgdk-pixbuf`, `fonts-noto` for Kannada/Marathi glyphs). These are installed automatically in the Docker image; for a native (non-Docker) setup on Debian/Ubuntu:

```bash
sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info fonts-noto
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
- Curated handover doc for the Android team: [HANDOVER.md](HANDOVER.md)

## Core Endpoints

| Method | Path                                | Description                                  |
|--------|-------------------------------------|-----------------------------------------------|
| POST   | `/api/v1/auth/signup`               | Set a PIN for an invited phone number, issue JWT pair |
| POST   | `/api/v1/auth/login`                | Login with phone number + PIN                |
| POST   | `/api/v1/auth/logout`               | Blacklist a refresh token                    |
| POST   | `/api/v1/auth/refresh`              | Exchange refresh token for new access token  |
| POST   | `/api/v1/auth/change-pin`           | Change the caller's own PIN                  |
| GET/PUT| `/api/v1/users/me`                  | Fetch/update current user profile            |
| POST   | `/api/v1/members/invite`            | Invite a phone number as admin/member (admin only) |
| GET    | `/api/v1/members/`                  | List members, filter by status/role/search (admin only) |
| POST   | `/api/v1/members/{id}/suspend`      | Suspend a member with a reason (admin only)  |
| POST   | `/api/v1/members/{id}/reactivate`   | Reactivate a member with a reason (admin only)|
| POST   | `/api/v1/members/{id}/deactivate`   | Mark a member inactive (admin only)          |
| GET/POST| `/api/v1/categories/`              | List (any member) / create (admin) donation categories |
| GET/PUT/PATCH| `/api/v1/categories/{id}/`     | View / edit a category (edit admin only)     |
| GET/POST| `/api/v1/donations/`               | List own/all donations, record a new one     |
| GET/PUT/PATCH| `/api/v1/donations/{id}/`      | View/edit a donation (owner or admin)        |
| GET    | `/api/v1/receipts/{donation_id}/`   | Receipt data as JSON                         |
| GET    | `/api/v1/receipts/{donation_id}/pdf`| Download/reprint the PDF receipt (`?language=`)|
| GET    | `/api/v1/reports/summary`           | Total collection, cash vs UPI, count (admin only) |
| GET    | `/api/v1/reports/category`          | Category-wise collection + goal progress (admin only) |
| GET    | `/api/v1/reports/member`            | Member-wise collection (admin only)          |
| GET    | `/api/v1/reports/date`              | Date-wise collection (admin only)            |
| GET/PUT| `/api/v1/temple-settings/`          | Temple identity/receipt config (edit admin only) |
| GET    | `/health`                           | Liveness/readiness probe (db, cache, version, uptime) |

All responses use a uniform envelope:

```json
{"success": true, "message": "Login successful", "data": {}}
```

```json
{"success": false, "error": {"code": "INVALID_CREDENTIALS", "message": "Phone number or PIN is incorrect."}}
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

Tests live alongside each app in `apps/<app>/tests/` (`test_models.py`, `test_serializers.py`, `test_services.py`, `test_views.py`) plus `core/tests/` for cross-cutting concerns (exception handler, health check). Fixtures and factories: `conftest.py` (root), `apps/users/tests/factories.py`, `apps/donations/tests/factories.py` (factory-boy).

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
- **Signup returns `NOT_INVITED`**: the phone number has no pending invitation - an admin must call `POST /api/v1/members/invite` first.
- **Login returns `ACCOUNT_SUSPENDED`/`ACCOUNT_PENDING`/`ACCOUNT_INACTIVE`**: the member's `status` isn't `ACTIVE` - check `/api/v1/members/{id}/` or the Django admin.
- **401 on every authenticated request**: check `Authorization: Bearer <access_token>` header and that `JWT_SECRET`/`SIMPLE_JWT` settings match between token issuance and verification.
- **Receipt PDF endpoint 500s**: confirm WeasyPrint's native libraries are installed (see Setup) and that `pydyf` is pinned to `<0.12` (`pydyf>=0.12` breaks WeasyPrint 62.x's PDF stream generation).
- **Coverage gate fails in CI**: run `pytest` locally and inspect `htmlcov/index.html` for uncovered lines.
