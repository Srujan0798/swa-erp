# API Reference

Live OpenAPI docs: `http://localhost:8000/docs` (Swagger UI)
Alternative: `http://localhost:8000/redoc`

This file describes the API at a higher level. The OpenAPI spec is the source of truth for exact request/response shapes.

## Conventions

- **Base path:** `/api`
- **Auth:** `Authorization: Bearer <jwt>` for all endpoints except `/api/auth/login`, `/api/auth/refresh`, `/healthz`, `/readyz`
- **Content type:** `application/json` for requests and responses (except file uploads which use `multipart/form-data`)
- **Pagination:** `?page=1&page_size=20`; default 20, max 100. Response includes `{items, total, page, page_size}`
- **Errors:** `{detail: string, code?: string, request_id: string}` with appropriate HTTP status
- **Request ID:** every response includes `X-Request-ID` header (echoes the request's, or generates one)
- **Dates:** ISO 8601 with `Z` suffix in responses; accepts ISO 8601 in requests

## Surface by wave

### Wave 1 — Foundation
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `GET  /api/auth/me`
- `GET  /api/users` (admin)
- `POST /api/users` (admin)
- `GET  /api/users/{id}` (admin or self)
- `PATCH /api/users/{id}` (admin or self)
- `DELETE /api/users/{id}` (admin)
- `GET  /healthz`
- `GET  /readyz`

### Wave 2 — Clients + Projects
- `GET/POST/PATCH/DELETE /api/clients`
- `GET/POST/PATCH/DELETE /api/projects`
- `POST /api/projects/{id}/transition` (lifecycle state change)

### Wave 3 — Quotation/BOQ
- `POST /api/projects/{id}/boq/upload` (multipart, JSON or Excel)
- `GET /api/projects/{id}/boq/versions`
- `POST /api/quotes` (generate from BOQ)
- `POST /api/quotes/{id}/send`
- `GET /api/quotes/{id}/pdf`

### Wave 4 — Tasks
- `GET/POST/PATCH/DELETE /api/tasks`
- `POST /api/tasks/{id}/assign`
- `POST /api/tasks/{id}/depends-on`

### Wave 5+ — see future spec files

## Auth flow (full)

```
1. Client → POST /api/auth/login {email, password}
2. Server: bcrypt-verify password
3. Server: issue access (1h) + refresh (30d); store refresh hash
4. Server: audit_log entry "auth.login_success"
5. Server → Client {access_token, refresh_token, user}

6. Client stores tokens in localStorage
7. Client makes requests with Authorization: Bearer <access>
8. Server: decode JWT, check exp, load user, check is_active

9. Access token expires after 1h
10. Client → POST /api/auth/refresh {refresh_token}
11. Server: verify refresh hash exists, not revoked, not expired
12. Server → Client {access_token}

13. On logout: POST /api/auth/logout (bearer)
14. Server: revoke refresh token (set revoked_at)
15. Server: audit_log entry "auth.logout"
```

## Status codes used
- `200` OK — success
- `201` Created — new resource (POST)
- `204` No Content — success without body (DELETE)
- `400` Bad Request — malformed input
- `401` Unauthorized — missing/invalid/expired token
- `403` Forbidden — token valid but insufficient role
- `404` Not Found — resource doesn't exist
- `409` Conflict — uniqueness violation, optimistic lock mismatch
- `422` Unprocessable Entity — Pydantic validation error
- `429` Too Many Requests — rate limit (later wave)
- `500` Server Error — bug
- `503` Service Unavailable — DB down (`/readyz` returns this when DB unhealthy)
