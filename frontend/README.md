## VidyaSetu Frontend

React + Vite frontend for the VidyaSetu full-stack app.

### Prerequisites

- Node.js + npm

### Environment

Create `frontend/.env` (or copy from `frontend/.env.example`):

- `VITE_API_BASE_URL` - backend origin, without `/api/v1` (default `http://localhost:8000`)

### Run (dev)

```sh
# from frontend/
npm i
npm run dev
```

Vite dev server runs on `http://localhost:8080` (see `vite.config.ts`).

### Backend dev

From `backend/`:

```sh
pip install -e ".[dev]"
python -m alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload
```

Default seeded users (see `backend/README.md`):

- Admin: `admin@vidyasetu.edu` / `admin123`
- Institution admin: `institution.admin@vidyasetu.edu` / `institution123`
- Educator: `educator@vidyasetu.edu` / `educator123`
- Student: `student@vidyasetu.edu` / `student123`

### Auth flow

Frontend uses the backend JWT flow:

- `POST /api/v1/auth/login`
- `GET /api/v1/users/me`
- `POST /api/v1/auth/refresh`

