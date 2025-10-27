
# Lead Intake Service (FastAPI)

A production-style FastAPI application to collect **public leads** and power an **internal authenticated API** for attorneys.
It supports file uploads (resume/CV), persistent storage, email notifications, and lead state management.

---

## Features

- Public endpoint to create a lead (first/last name, email, resume/CV file).
- Emails sent to both the prospect and the in-house attorney on submission.
- Internal authenticated endpoints (JWT) to list, get, and update lead state (PENDING → REACHED_OUT).
- SQLite by default; configurable DB via `DATABASE_URL` (Postgres, MySQL, etc.).
- File uploads saved to disk with secure filenames.
- Optional SMTP email via environment variables; or use **console** backend that writes `.eml` files to `./outbox/`.
- Alembic migrations included.
- Clean, modular, production-style repo structure.
- OpenAPI docs at `/docs` and `/redoc`.

---

## Quickstart (Local)

### 1) Prereqs
- Python **3.11+**

### 2) Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# You can leave MAILER_BACKEND=console (default) to write emails to ./outbox/
# Or run a local SMTP server (see below) and set MAILER_BACKEND=smtp
```

### 3) Init DB
```bash
alembic upgrade head
```

### 4) Run the API
```bash
uvicorn app.main:app --reload
```

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 5) Try It

#### Obtain a JWT (attorney login)
```bash
curl -X POST "http://localhost:8000/auth/token" -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=attorney@example.com&password=secret"
```

#### Create a Lead (public)
```bash
curl -X POST "http://localhost:8000/public/leads" -F first_name=Jane -F last_name=Doe -F email=jane@example.com \
  -F resume=@/path/to/resume.pdf
```

#### List Leads (internal; token required)
```bash
TOKEN=... # paste your access_token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/leads
```

#### Mark Lead REACHED_OUT
```bash
curl -X PATCH "http://localhost:8000/leads/<LEAD_ID>/state" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"state":"REACHED_OUT"}'
```

### Optional: Run a Local SMTP (MailHog)

Run MailHog with Docker:
```bash
docker run -d -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog
```
- Set in `.env`: `MAILER_BACKEND=smtp`, `SMTP_HOST=localhost`, `SMTP_PORT=1025`
- UI: http://localhost:8025

---

## Repo Structure

```
app/
  auth.py
  config.py
  database.py
  deps.py
  emailer.py
  main.py
  models.py
  schemas.py
  services/lead_service.py
  utils/
    security.py
    storage.py
  routers/
    public.py
    leads.py
    files.py
alembic/
  env.py
  script.py.mako
  versions/
    <timestamp>_initial.py
tests/
  test_leads.py
```

---

## Design

See [DESIGN.md](DESIGN.md) for a detailed system design covering architecture, trade-offs, and future improvements.

---

## Notes

- Default attorney login (dev): `attorney@example.com` / `secret` (seeded on startup).
- Uploaded resumes are saved under `./uploads` and downloadable through an **authenticated** endpoint.
- The console email backend writes `.eml` files into `./outbox` for easy inspection.
