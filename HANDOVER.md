# TDMS Backend — Android Handover Doc

This document is the API contract for the Android team building the Temple Donation Management System (TDMS) client. It covers authentication, every endpoint, request/response shapes, error codes, enums, pagination, and file downloads (receipt PDFs, report exports).

The backend also publishes a live, interactive OpenAPI spec — prefer it once the server is reachable, since it can never drift from this doc:

- Swagger UI: `GET /api/docs/`
- ReDoc: `GET /api/redoc/`
- Raw schema (for codegen, e.g. Retrofit/OpenAPI generators): `GET /api/schema/`

## 1. Base URL & versioning

All application endpoints are namespaced under `/api/v1/`. Example (local dev): `http://10.0.2.2:8000/api/v1/...` (`10.0.2.2` is the Android emulator's alias for the host machine's `localhost`).

## 2. Response envelope

Every endpoint — success or failure — returns this shape. **Always branch on `success`, never on HTTP status code alone**, though the status code is also set correctly (200/201/400/401/403/404/409/500).

Success:
```json
{
  "success": true,
  "message": "Human-readable summary",
  "data": { }
}
```

Error:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "amount: A valid number is required.",
    "details": { "amount": ["A valid number is required."] }
  }
}
```

`details` is present for field-level validation errors and omitted otherwise.

## 3. Error codes

| Code | HTTP status | Meaning |
|---|---|---|
| `VALIDATION_ERROR` | 400 | Request body/query failed validation |
| `AUTHENTICATION_ERROR` | 401 | Missing/invalid auth |
| `INVALID_TOKEN` | 401 | JWT malformed/invalid |
| `TOKEN_EXPIRED` | 401 | Refresh token expired, invalid, or already blacklisted |
| `INVALID_CREDENTIALS` | 401 | Login: unknown phone number or wrong PIN (deliberately not distinguished, to avoid leaking which one is wrong) |
| `PERMISSION_DENIED` | 403 | Authenticated, but role/status doesn't allow this action |
| `NOT_INVITED` | 403 | Signup attempted for a phone number with no pending invitation |
| `ACCOUNT_PENDING` | 403 | Login attempted before completing signup (PIN not set yet) |
| `ACCOUNT_SUSPENDED` | 403 | Login attempted on a suspended account (message includes the reason, if one was given) |
| `ACCOUNT_INACTIVE` | 403 | Login attempted on a deactivated account |
| `NOT_FOUND` | 404 | Resource doesn't exist (or isn't visible to you) |
| `ALREADY_REGISTERED` | 409 | Signup attempted for a phone number that already completed signup |
| `DUPLICATE_INVITATION` | 409 | Invite attempted for a phone number already active or already invited |
| `INTEGRITY_ERROR` | 409 | Database constraint violation |
| `THROTTLED` | 429 | Rate limit hit (see §11) |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## 4. Authentication

**No OTP/SMS.** Auth is phone number + a 6-digit PIN, the same UX pattern as a UPI app's MPIN: an admin invites a phone number, that person signs up once by choosing a PIN, and logs in with phone + PIN from then on. All authenticated endpoints expect:

```
Authorization: Bearer <access_token>
```

Access tokens expire in 15 minutes by default (`JWT_ACCESS_EXPIRY_MINUTES`); refresh tokens in 7 days (`JWT_REFRESH_EXPIRY_DAYS`) and rotate on every use (the old refresh token is blacklisted the moment you refresh — store the new one).

### 4.1 `POST /api/v1/auth/signup` — first-time PIN set-up

Only works for a phone number an admin has already invited (see §6.1). `role`/`name` are not accepted here — `name` is captured, role comes from the invite.

Request:
```json
{
  "phone_number": "+919876543210",
  "pin": "123456",
  "confirm_pin": "123456",
  "name": "Ravi Kumar"
}
```

Response `200`:
```json
{
  "success": true,
  "message": "Signup successful",
  "data": {
    "access": "eyJhbGciOi...",
    "refresh": "eyJhbGciOi...",
    "user": {
      "id": "60050b35-f353-4faf-ab8d-054015e794bc",
      "phone_number": "+919876543210",
      "name": "Ravi Kumar",
      "role": "MEMBER",
      "status": "ACTIVE",
      "suspension_reason": "",
      "suspended_at": null,
      "created_at": "2026-08-04T18:02:55.654110Z",
      "updated_at": "2026-08-04T18:02:55.654119Z"
    }
  }
}
```

Failure modes: `NOT_INVITED` (403) if the phone was never invited; `ALREADY_REGISTERED` (409) if it already completed signup; `VALIDATION_ERROR` (400) if `pin` isn't exactly 6 digits or doesn't match `confirm_pin`.

### 4.2 `POST /api/v1/auth/login`

Request:
```json
{ "phone_number": "+919876543210", "pin": "123456" }
```

Response `200`: identical shape to signup's `data` (access/refresh/user).

Failure modes: `INVALID_CREDENTIALS` (401, unknown phone or wrong PIN), `ACCOUNT_PENDING` (403, hasn't signed up yet), `ACCOUNT_SUSPENDED` (403, includes reason in the message), `ACCOUNT_INACTIVE` (403).

### 4.3 `POST /api/v1/auth/refresh`

Request: `{ "refresh": "<refresh_token>" }`
Response `200`: `{ "access": "...", "refresh": "..." }` (new refresh token — the old one is now invalid).

### 4.4 `POST /api/v1/auth/logout`

Request: `{ "refresh": "<refresh_token>" }` → blacklists it server-side. Response `200`, no `data`.

### 4.5 `POST /api/v1/auth/change-pin` — requires auth

Request: `{ "old_pin": "123456", "new_pin": "654321" }` → `INVALID_CREDENTIALS` if `old_pin` is wrong.

## 5. Roles & member status

Two roles (`UserRole`): `ADMIN`, `MEMBER`. Admins manage members/categories/settings and see all reports; Members add donations and see only their own.

Four lifecycle statuses (`MemberStatus`), tracked on the user record:

| Status | Meaning |
|---|---|
| `PENDING` | Invited, hasn't completed signup (no usable PIN yet) |
| `ACTIVE` | Can log in and use the API |
| `SUSPENDED` | Login blocked; `suspension_reason`/`suspended_at` populated |
| `INACTIVE` | Login blocked (soft off-boarding, no reason required) |

Only `ACTIVE` accounts can log in or call any endpoint gated by `IsActiveMember`.

## 6. Members (admin only, except `me`)

### 6.1 `POST /api/v1/members/invite`

Request: `{ "phone_number": "+919876543210", "role": "MEMBER" }` (`role` defaults to `MEMBER`; pass `"ADMIN"` to invite another admin).

Response `200`:
```json
{
  "success": true,
  "message": "Invitation sent",
  "data": {
    "id": "5c9585a2-1d79-49aa-a6e5-62599fe99e2e",
    "phone_number": "+919876543210",
    "role": "MEMBER",
    "status": "PENDING",
    "created_at": "2026-08-04T18:02:55.654849Z",
    "accepted_at": null
  }
}
```

### 6.2 `GET /api/v1/members/` — paginated list

Query params: `status`, `role`, `search` (matches name or phone). See §10 for the pagination envelope.

### 6.3 `GET /api/v1/members/{id}/` — single member detail

### 6.4 `POST /api/v1/members/{id}/suspend` — `{ "reason": "..." }` (required)
### 6.5 `POST /api/v1/members/{id}/reactivate` — `{ "reason": "..." }` (required)
### 6.6 `POST /api/v1/members/{id}/deactivate` — `{ "reason": "..." }` (required)

All three return the updated member object, same shape as §6.2's rows.

### 6.7 `GET /api/v1/users/me` / `PUT /api/v1/users/me` — any authenticated user

`PUT` only accepts `{ "name": "..." }` — phone number and role are not editable via this endpoint.

## 7. Donation categories

### 7.1 `GET /api/v1/categories/` — any active member

Query param: `?is_active=true|false` (omit for all).

```json
{
  "success": true,
  "message": "Success",
  "data": [
    {
      "id": "a92ba265-b634-46e9-90a3-8bf9f17d98ca",
      "name": "Annadanam",
      "description": "",
      "is_active": true,
      "goal_amount": "100000.00",
      "color": "#FF5733",
      "sort_order": 0,
      "collected_amount": 1502.0,
      "progress_percent": 1.5,
      "created_at": "2026-08-04T18:04:10.239713Z",
      "updated_at": "2026-08-04T18:04:10.239731Z"
    }
  ]
}
```

`collected_amount`/`progress_percent` are computed live from donations against this category. `progress_percent` is `null` when `goal_amount` is unset. Donations continue to be accepted past 100%.

### 7.2 `POST /api/v1/categories/` — admin only

Request: `{ "name": "Hundi", "description": "", "goal_amount": "5000.00", "color": "#FF5733", "sort_order": 1 }` — all fields except `name` are optional.

### 7.3 `GET /api/v1/categories/{id}/` — any active member
### 7.4 `PUT` / `PATCH /api/v1/categories/{id}/` — admin only, same body shape as 7.2 (PATCH accepts a partial subset)

## 8. Donations

Amounts are strings (`"501.00"`), not floats, to avoid precision loss — parse as `BigDecimal` on Android, not `Double`.

### 8.1 `GET /api/v1/donations/` — paginated

- **Members** see only their own entries (`collected_by == you`), always — there's no way to widen this.
- **Admins** see everyone's, and can filter by `collected_by=<user_id>`.
- Shared filters: `category`, `payment_mode` (`CASH`/`UPI`), `date_from`, `date_to` (`YYYY-MM-DD`), `search` (matches donor name, donor phone, or receipt number).

### 8.2 `POST /api/v1/donations/` — any active member

Request:
```json
{
  "donation_date": "2026-08-04",
  "donor_name": "Suresh Rao",
  "donor_phone": "",
  "donor_address": "",
  "category": "a92ba265-b634-46e9-90a3-8bf9f17d98ca",
  "amount": "501.00",
  "payment_mode": "CASH",
  "utr_number": "",
  "remarks": "",
  "receipt_language": "EN"
}
```

- `donation_date` defaults to today if omitted.
- `donor_phone`/`donor_address`/`remarks` are optional.
- `utr_number` is **required when `payment_mode` is `"UPI"`** — omitting it returns `VALIDATION_ERROR` with `details.utr_number`.
- `receipt_language` is one of `EN`/`KN`/`MR` (default `EN`) — this is what the PDF receipt renders in by default (overridable per-download, see §9.2).
- `collected_by` and `receipt_number` are never sent by the client — the server sets `collected_by` to the caller and generates `receipt_number` atomically (format `TDMS-000001`, sequential, gapless under concurrent writes).

Response `201`:
```json
{
  "success": true,
  "message": "Donation recorded",
  "data": {
    "id": "e571225a-544f-47aa-98c2-75b005ba95b8",
    "receipt_number": "TDMS-000001",
    "donation_date": "2026-08-04",
    "donor_name": "Suresh Rao",
    "donor_phone": "",
    "donor_address": "",
    "category": { "...": "same shape as §7.1" },
    "amount": "501.00",
    "payment_mode": "CASH",
    "utr_number": "",
    "remarks": "",
    "receipt_language": "EN",
    "collected_by": { "...": "same shape as §6.2 rows" },
    "created_at": "2026-08-04T18:04:49.375493Z",
    "updated_at": "2026-08-04T18:04:49.375501Z"
  }
}
```

### 8.3 `GET /api/v1/donations/{id}/` — owner or admin (403 for anyone else)
### 8.4 `PUT` / `PATCH /api/v1/donations/{id}/` — owner or admin, same body as 8.2 (partial for PATCH)

Edits are audit-logged server-side (money is involved) — nothing extra required from the client.

## 9. Receipts

### 9.1 `GET /api/v1/receipts/{donation_id}/` — JSON, owner or admin

Same shape as a donation object (§8.2's response `data`) — useful for a receipt preview screen before printing.

### 9.2 `GET /api/v1/receipts/{donation_id}/pdf` — binary PDF, owner or admin

- `Content-Type: application/pdf`, `Content-Disposition: attachment; filename="TDMS-000001.pdf"`.
- Optional `?language=EN|KN|MR` overrides the donation's stored `receipt_language` for a one-off reprint in another language, without changing the record.
- A5-sized single page: temple logo/name/address, receipt no., date, donor details, category, amount, payment mode (+ UTR if UPI), collector name, signature line, footer thank-you text — all localized per language.
- On Android, download via your HTTP client with the `Authorization` header set, save the response body as a `.pdf`, and open it with an intent (`ACTION_VIEW`, MIME `application/pdf`) or a PDF-rendering library for in-app preview/print.

## 10. Reports (admin only)

All four endpoints accept the same filters as query params: `date_from`, `date_to`, `category` (category id), `member` (user id), `payment_mode`. Add `?export=csv|excel|pdf` to get a downloadable file instead of JSON (same filters apply) — response `Content-Type` becomes `text/csv`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, or `application/pdf` respectively, with `Content-Disposition: attachment`.

### 10.1 `GET /api/v1/reports/summary`
```json
{ "total_collection": 1502.0, "donation_count": 2, "cash_total": 501.0, "upi_total": 1001.0 }
```

### 10.2 `GET /api/v1/reports/category`
```json
[{
  "category_id": "a92ba265-...", "category_name": "Annadanam",
  "goal_amount": 100000.0, "collected_amount": 1502.0,
  "donation_count": 2, "progress_percent": 1.5
}]
```

### 10.3 `GET /api/v1/reports/member`
```json
[{
  "member_id": "60050b35-...", "member_name": "Ravi Kumar",
  "phone_number": "+919876543210", "total_collected": 1502.0, "donation_count": 2
}]
```

### 10.4 `GET /api/v1/reports/date`
```json
[{ "date": "2026-08-04", "total_collected": 1502.0, "donation_count": 2, "cash_total": 501.0, "upi_total": 1001.0 }]
```

Note: unlike the donation/category endpoints, report row numbers here are JSON floats, not strings — fine for display, but re-verify precision server-side before using these for anything beyond display (e.g. don't use report totals as a source of truth for reconciliation; sum the underlying donations instead).

## 11. Temple settings

### 11.1 `GET /api/v1/temple-settings/` — any active member

```json
{
  "id": "...", "temple_name": "Sri Test Temple", "address": "", "phone": "", "email": "",
  "logo_url": "", "signature_url": "", "registration_number": "", "currency_symbol": "₹",
  "receipt_prefix": "TDMS"
}
```

Fetch this once (e.g. on app start / dashboard load) for the temple name/logo to show in the app header and receipt preview.

### 11.2 `PUT /api/v1/temple-settings/` — admin only

Partial update, any subset of the fields above (excluding `id`).

## 12. Pagination

Endpoints that list many rows (`/members/`, `/donations/`) wrap results like this:

```json
{
  "success": true,
  "message": "Success",
  "data": {
    "count": 42,
    "next": "http://.../api/v1/donations/?page=2",
    "previous": null,
    "results": [ /* rows */ ]
  }
}
```

Default page size 20, override with `?page_size=`, capped at 100. `/categories/` and the `/reports/*` endpoints are **not** paginated (they return a plain array/object in `data`) since result sets are small.

## 13. Rate limiting

`/auth/signup` and `/auth/login` are throttled separately from general API traffic (20/hour per IP by default, via `THROTTLE_SIGNUP`/`THROTTLE_LOGIN`). A `429` with `error.code == "THROTTLED"` includes a retry-after hint in the message. General authenticated traffic is throttled at 1000/hour/user, anonymous at 100/hour/IP.

## 14. Known caveats for the Android team

- **Kannada/Marathi label translations** in the PDF receipts are a best-effort machine translation of standard receipt terms (Receipt No., Donor Name, Amount, etc.) — have a native speaker sanity-check them before shipping to real temples.
- **No OTP/SMS gateway is wired up.** Auth is entirely PIN-based; there's no "forgot PIN" self-service flow yet — a locked-out member currently needs an admin to suspend+reactivate them isn't a PIN reset, so today the only path is asking the admin to re-invite via Django Admin/support if truly locked out. Flag this to product if self-service PIN reset is needed before launch.
- **Amounts are decimal strings** in donation/category payloads (`"501.00"`) but plain floats in the `/reports/*` endpoints — parse accordingly per endpoint.
- **A donation's `receipt_number` is permanent** even if the donation is later edited (amount, category, etc.) — reprints after an edit will show the updated data under the same receipt number.
