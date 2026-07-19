# Technical Requirements Document (TRD)

## Project Title

**Analyst Platform Backend API**

## Objective

Build a **production-grade Django REST Framework backend** that serves as the backend for an Android application.

The system should be designed using modern backend engineering principles including:

* Clean Architecture
* Modular apps
* RESTful API design
* JWT Authentication
* Google OAuth Login
* PostgreSQL
* Docker
* Production-ready logging
* Automated testing
* Proper exception handling
* API documentation
* High maintainability
* Scalable folder structure

The final output should resemble an enterprise backend that can easily scale from a few thousand users to millions.

---

# Technology Stack

## Language

Python 3.12+

---

## Framework

Django 5.x

Django Rest Framework

---

## Database

PostgreSQL 16+

Requirements

* UUID Primary Keys
* Proper Indexes
* Foreign Keys
* Constraints
* Transactions where necessary

---

## Authentication

Google OAuth

JWT Authentication

Recommended libraries

* django-allauth OR google-auth
* djangorestframework-simplejwt

Refresh Tokens should be implemented.

---

## API Style

REST APIs only.

JSON Requests.

JSON Responses.

HTTP status codes must strictly follow REST conventions.

---

## Deployment

Docker

Docker Compose

Gunicorn

Nginx Ready

---

## API Documentation

Swagger/OpenAPI

Recommended

drf-spectacular

Requirements

* Every endpoint documented
* Request examples
* Response examples
* Error responses

---

# High Level Architecture

```
Android App

        |

 REST APIs

        |

 Django REST Framework

        |

 Business Services Layer

        |

Repositories / ORM

        |

 PostgreSQL
```

Every layer should have clear responsibility.

No business logic inside Views.

Views should only:

* authenticate
* validate
* invoke service
* return response

---

# Folder Structure

```
backend/

    config/
        settings/
            base.py
            dev.py
            prod.py

        urls.py
        asgi.py
        wsgi.py

    apps/

        common/
        users/
        authentication/
        analytics/
        subscribers/
        notifications/

    core/
        exceptions/
        middleware/
        permissions/
        pagination/
        logging/
        validators/
        constants/

    services/

    utils/

    tests/

    docker/

    scripts/

    manage.py
```

Apps must remain independent.

Avoid circular dependencies.

---

# Environment Variables

Everything configurable.

Example

```
DEBUG

SECRET_KEY

DATABASE_URL

GOOGLE_CLIENT_ID

GOOGLE_CLIENT_SECRET

JWT_SECRET

JWT_ACCESS_EXPIRY

JWT_REFRESH_EXPIRY

ALLOWED_HOSTS

LOG_LEVEL

SENTRY_DSN
```

Never hardcode secrets.

---

# Coding Standards

PEP8

Type Hinting

Docstrings

Black formatting

isort

flake8

mypy compatible

No duplicated code.

Maximum function size:

50 lines

Maximum class size:

300 lines

Business logic must remain inside Service layer.

---

# Database Design

Use UUID everywhere.

Example

```
id

uuid

created_at

updated_at
```

All tables should include

created_at

updated_at

created_by (optional)

updated_by (optional)

soft_delete flag if applicable.

---

# User Module

## User Model

Custom Django User model.

Fields

```
id

email

first_name

last_name

profile_picture

phone_number

user_type

google_id

is_active

is_verified

last_login

created_at

updated_at
```

User Type Enum

```
ANALYST

SUBSCRIBER
```

Phone Number mandatory.

Email unique.

Google ID unique.

---

# Authentication Module

## Login Flow

Android

↓

Google Sign In

↓

Receive Google ID Token

↓

Backend Verify Token

↓

Create User if not exists

↓

Generate JWT

↓

Return Access Token

↓

Return Refresh Token

---

# APIs

---

## POST

/api/v1/auth/google/login

Request

```
{
    "id_token": "...",
    "phone_number": "...",
    "user_type":"ANALYST"
}
```

Backend

Verify token

If user exists

login

Else

create account

Return

```
{
    "access":"...",
    "refresh":"...",
    "user":{}
}
```

---

## POST

/auth/logout

Blacklist refresh token.

Return success.

---

## POST

/auth/refresh

Return new access token.

---

## GET

/users/me

Current profile.

---

## PUT

/users/me

Update profile.

Editable

PhoneProfile photo

Name

Not editable

Email

Google ID

User Type

---

# Validation Rules

Phone mandatory.

Email mandatory.

User Type mandatory.

Google Token mandatory.

Reject invalid values.

---

# Serializer Guidelines

Every endpoint must have

Request Serializer

Response Serializer

Never use

```
fields="__all__"
```

Explicit fields only.

Validation inside serializers only.

Business logic inside service layer.

---

# Service Layer Pattern

Example

```
GoogleAuthService

UserService

TokenService

NotificationService
```

Views call Services.

Services call ORM.

No ORM in Views.

---

# Response Format

Success

```
{
    "success": true,
    "message": "Login successful",
    "data": {}
}
```

Failure

```
{
    "success": false,
    "error": {
        "code":"INVALID_TOKEN",
        "message":"Google token invalid"
    }
}
```

Uniform response everywhere.

---

# Exception Handling

Implement global exception handler.

Handle

Validation Error

Authentication Error

Permission Error

Object Not Found

Integrity Error

Unhandled Exception

Map every exception into API response.

Never expose stack trace.

---

# Logging

Use Python logging module.

Structured logging.

JSON format.

Every request should log

Timestamp

Method

URL

Response Time

Status

User ID

IP

Request ID

Every exception logged.

Log levels

DEBUG

INFO

WARNING

ERROR

CRITICAL

Support rotating log files.

Production compatible.

---

# Middleware

Implement

Request ID Middleware

Response Time Middleware

Request Logging Middleware

Security Headers Middleware

---

# Security

HTTPS Ready

JWT Authentication

CSRF disabled for APIs

Rate limiting

CORS

Secure Cookies (future)

Input sanitization

SQL Injection protection

XSS protection

Brute force protection

Google token verification

Password login not required.

---

# Permissions

Anonymous

Authenticated

Admin

Analyst

Subscriber

Role based permissions.

Custom DRF permission classes.

---

# Pagination

Page Number Pagination

Default

20

Maximum

100

---

# Filtering

DRF Filters

Ordering

Searching

---

# API Versioning

```
/api/v1/
```

Future

```
/api/v2/
```

---

# Testing

Use

pytest

pytest-django

factory-boy

coverage

---

## Tests Required

Unit Tests

Serializer Tests

Service Tests

Permission Tests

Authentication Tests

API Tests

Integration Tests

---

Coverage

Minimum

90%

---

Test Cases

Google Login Success

Google Login Failure

Missing Phone

Missing User Type

Duplicate User

Invalid JWT

Expired JWT

Logout

Refresh Token

Profile Fetch

Profile Update

Permission Failure

Validation Failure

---

# Docker

docker-compose should include

```
backend

postgres

redis (future)

nginx (optional)
```

---

Dockerfile Requirements

Multi-stage build

Small image

Non-root user

Health checks

Environment variables

Volume support

---

# Database Migration

Every model must have migrations.

Migration names meaningful.

No manual SQL.

---

# Performance

select_related()

prefetch_related()

Proper indexes

Avoid N+1 queries

Bulk operations where possible

Transactions where required

---

# Monitoring Ready

Support

Sentry

Prometheus (future)

Health API

```
GET

/health
```

Returns

```
Database

Redis

Application

Version

Uptime
```

---

# CI/CD Ready

Project should support

GitHub Actions

Pipeline

```
Lint

↓

Unit Tests

↓

Coverage

↓

Build Docker

↓

Push Image
```

---

# Documentation

README should include

Project setup

Docker setup

Environment variables

API documentation

Folder structure

Deployment

Testing

Database migrations

Coding guidelines

Troubleshooting

---

# Dependencies

Core

* Django
* Django REST Framework
* psycopg
* SimpleJWT
* drf-spectacular
* django-filter
* google-auth
* python-dotenv
* gunicorn

Development

* pytest
* pytest-django
* coverage
* black
* isort
* flake8
* mypy
* factory-boy
* Faker

---

# Deliverables

The generated codebase must include:

1. Production-ready Django project structure.
2. PostgreSQL integration with UUID-based schema.
3. Custom User model with Analyst and Subscriber roles.
4. Google OAuth authentication flow suitable for Android clients.
5. JWT authentication with access and refresh tokens.
6. Logout and token refresh endpoints.
7. Profile management APIs.
8. Modular architecture with clear separation of concerns (Views → Serializers → Services → Models).
9. Global exception handling with standardized API responses.
10. Structured JSON logging with request IDs and performance metrics.
11. Security best practices including CORS, rate limiting, and input validation.
12. Swagger/OpenAPI documentation for every endpoint.
13. Dockerized local development and production configuration.
14. Comprehensive pytest-based test suite achieving at least 90% code coverage.
15. Health check endpoint and production deployment readiness.
16. CI/CD-ready configuration with linting, testing, Docker build support, and documentation.

---

# Success Criteria

The completed backend should be:

* Production-ready and deployable without architectural refactoring.
* Fully Dockerized with PostgreSQL support.
* Secure, scalable, and maintainable.
* Capable of serving Android applications through well-designed REST APIs.
* Easy to extend by adding new Django apps without modifying existing modules.
* Well-tested, well-documented, and compliant with enterprise backend engineering standards.
