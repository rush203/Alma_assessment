
# System Design – Lead Intake Service

## Goals
Collect leads from a public form and notify both the prospect and the in-house attorney, while providing an internal (authenticated) API to manage leads and their state.

## High-Level Architecture
```
[ Client / Prospect ] --(POST multipart/form-data)--> [ FastAPI App ] --> [ Storage (DB + Files) ]
                                                             |  \
                                                             |   +--> [ Email Service (SMTP or Console) ]
                                                             |
                                                     [Attorney / Internal API (JWT)]
```

- **FastAPI** hosts public and internal routes.
- **Database** persists leads, users, and metadata.
- **File storage** (disk) stores resumes; DB stores file path.
- **Email service** abstracts SMTP vs console backend.
- **Auth**: OAuth2 + JWT for internal APIs (role-based: attorney).

## Data Model

### Lead
- `id`: UUID (string)
- `first_name`, `last_name`, `email`
- `resume_path`: str (relative path in uploads dir)
- `state`: enum { `PENDING`, `REACHED_OUT` }
- `notes`: optional text
- `created_at`, `updated_at`

### User
- `id`: UUID
- `email`, `full_name`
- `hashed_password`, `is_active`, `role`

## Flows

### Create Lead (Public)
1. Prospect submits multipart form with metadata + resume file.
2. App writes resume to `/uploads/<uuid>.<ext>`.
3. DB insert with `PENDING` state.
4. Background tasks:
   - Email prospect a confirmation.
   - Email the attorney with lead details and a link to view (API).
5. Response includes lead id.

### Internal Management (JWT)
- Attorney logs in to `/auth/token` to obtain JWT.
- List/search leads, view details, download resume file.
- Update a lead's state from `PENDING` → `REACHED_OUT` (validated transition).

## Email
- **SMTP** backend (configurable) or **console** backend (writes `.eml` files).
- Non-blocking via FastAPI `BackgroundTasks`.
- Templates (Jinja2) for simple, consistent emails.

## Security
- Public endpoint validates inputs (Pydantic) and enforces file size/extension checks.
- Authenticated endpoints protected by OAuth2/JWT.
- Role-based check for `attorney` role.
- Uploaded files stored with random UUID filenames to prevent path traversal, and served only via an authenticated route.
- CORS disabled by default, configurable if needed.
- Rate limiting can be added via proxy/gateway (e.g., Nginx/Envoy) or Starlette middleware.

## Scalability & Reliability
- Stateless app; can scale horizontally.
- DB can be swapped to Postgres by changing `DATABASE_URL`.
- For file storage at scale, move to S3 or GCS and store signed URLs.
- Email retries/backoff can be added; or use a queue like Redis + RQ/Celery for robustness.
- Alembic for schema evolution.

## Observability
- Structured logging (uvicorn/fastapi).
- Return correlation IDs via middleware (future work).
- Add metrics (Prometheus) as a future improvement.

## Testing
- Pytest tests for key flows (create lead, list, state update).
- Use a temporary SQLite database for tests.

## Trade-offs
- Using SQLite by default for simplicity; can be replaced with managed DB in prod.
- BackgroundTasks vs external queue: simpler, but less robust if process crashes.
- Storing files locally is convenient for local dev; S3 recommended in prod.

## Future Improvements
- Add pagination, sorting, and more filters to list leads.
- Add email delivery status tracking and retries.
- Add auditing (lead history / events table).
- Multi-tenant / multi-attorney support with assignment workflow.
- Webhook or Slack notification integration.
