# VidyaSetu Backend

FastAPI + SQLAlchemy async backend for the VidyaSetu full-stack application.

Local development now defaults to SQLite. PostgreSQL can still be used later by changing `DATABASE_URL`.

## Development

1. Create `backend/.env` from `backend/.env.example`.
2. Install dependencies:

```sh
pip install -e ".[dev]"
```

3. Run migrations:

```sh
python -m alembic upgrade head
```

For the default SQLite setup, the app and seed script will also auto-create tables on first run. Alembic can still be used later when you formalize migrations.

4. Seed baseline users:

```sh
python -m scripts.seed
```

For a full local demo dataset across all core tables, use:

```sh
python -m scripts.test_data
```

This resets the SQLite database, recreates the schema, and loads linked demo data for institutions, users, workshops, modules, enrollments, sessions, attendance, assessments, questions, submissions, certificates, fees, payments, and notifications.

5. Start the API:

```sh
uvicorn app.main:app --reload
```

This will create `backend/vidyasetu.db` locally when using the default SQLite configuration.

## GenAI setup (Admin AI Reports)

GenAI configuration is backend-only. Add your Gemini key in `backend/.env`.

Required env vars:

```env
GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
GEMINI_MODEL_NAME=gemini-3.1-flash-lite-preview
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com
GEMINI_TIMEOUT_SECONDS=30
AI_MAX_RETRIES=3
AI_RETRY_BASE_DELAY_SECONDS=0.5
AI_ADMIN_REPORT_CACHE_TTL_SECONDS=3600
AI_ADMIN_REPORT_PROMPT_VERSION=v1
AI_ADMIN_REPORT_USER_RATE_LIMIT=3
AI_ADMIN_REPORT_INSTITUTION_RATE_LIMIT=10
AI_ADMIN_REPORT_RATE_LIMIT_WINDOW_SECONDS=600
AI_ADMIN_REPORT_STALE_AFTER_SECONDS=900
AI_RATE_LIMIT_BACKEND=database
AI_RATE_LIMIT_COUNTER_RETENTION_SECONDS=86400

# Async job system (Celery + Redis)
REDIS_URL=rediss://:<password>@<host>:<port>
```

Production notes:

- Keep `GEMINI_MODEL_NAME` on a stable version (`gemini-3.1-flash-lite-preview`).
- Keep `AI_RATE_LIMIT_BACKEND=database` for multi-instance-safe limits.
- `AI_RATE_LIMIT_BACKEND=memory` is only for local/single-process dev.
- Do not put Gemini keys in frontend env files.

After updating `.env`, run:

```sh
python -m alembic upgrade head
```

This creates/updates AI tables used by admin report generation and DB-backed rate limiting.

## Async AI jobs (Celery worker + beat)

AI report generation and student explanations run as background jobs.

1. Set `REDIS_URL` (Upstash supported via `rediss://`).
2. Start the API (`uvicorn app.main:app --reload`).
3. In a separate terminal, start a Celery worker:

```sh
celery -A app.jobs.celery_app.celery_app worker -l info -Q vidyasetu
```

4. For scheduled AI reports, also run Celery Beat:

```sh
celery -A app.jobs.celery_app.celery_app beat -l info
```

## Database options

- Default local DB: `sqlite+aiosqlite:///./vidyasetu.db`
- Optional later upgrade: set `DATABASE_URL` to a PostgreSQL URL such as `postgresql+asyncpg://postgres:postgres@localhost:5432/vidyasetu`

## Default seeded users

- Admin: `admin@vidyasetu.edu` / `admin123`
- Institution admin: `institution.admin@vidyasetu.edu` / `institution123`
- Educator: `educator@vidyasetu.edu` / `educator123`
- Student: `student2@vidyasetu.edu` / `demo123`

## Frontend integration

- API prefix: `/api/v1`
- Auth flow:
    - `POST /api/v1/auth/login`
    - `GET /api/v1/users/me`
    - `POST /api/v1/auth/refresh`
- Minimal password reset support:
    - `POST /api/v1/auth/forgot-password`
    - `POST /api/v1/auth/reset-password`

CORS is controlled by `FRONTEND_ORIGINS`, which should match the Vite dev origin(s).

## Dashboard endpoints

Used by the frontend dashboards:

- GET /api/v1/dashboard/admin (admin)
- GET /api/v1/dashboard/student/{student_id} (student self)
- GET /api/v1/dashboard/educator (staff)

## Certificates

- GET /api/v1/certificates/ (staff list)
- GET /api/v1/certificates/student/{student_id}
- GET /api/v1/certificates/verify/{verification_code} (public)
