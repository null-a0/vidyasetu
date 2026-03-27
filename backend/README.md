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

## Database options

- Default local DB: `sqlite+aiosqlite:///./vidyasetu.db`
- Optional later upgrade: set `DATABASE_URL` to a PostgreSQL URL such as `postgresql+asyncpg://postgres:postgres@localhost:5432/vidyasetu`

## Default seeded users

- Admin: `admin@vidyasetu.edu` / `admin123`
- Institution admin: `institution.admin@vidyasetu.edu` / `institution123`
- Educator: `educator@vidyasetu.edu` / `educator123`
- Student: `student@vidyasetu.edu` / `student123`

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

