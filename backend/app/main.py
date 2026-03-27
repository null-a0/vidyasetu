from __future__ import annotations
from fastapi.responses import Response
import yaml
import uvicorn

from contextlib import asynccontextmanager
from pathlib import Path

from app.api.v1 import api_router
from app.config import settings
from app.db import engine
from app.models import Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ---------------------------------------------------------------------------
# Lifespan: ensure media/ directory exists before requests start
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    Path("media").mkdir(exist_ok=True)
    if settings.DATABASE_URL.startswith("sqlite+"):
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    yield


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Static file serving for uploads  (mounted after media/ is guaranteed)
# ---------------------------------------------------------------------------

# also create at import time for hot-reload
Path("media").mkdir(exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

# ---------------------------------------------------------------------------
# API routers — all under /api/v1
# ---------------------------------------------------------------------------

app.include_router(api_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/", tags=["health"])
async def health() -> dict:
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/openapi.yaml", response_class=Response, include_in_schema=False)
def get_openapi_yaml():
    openapi_spec = app.openapi()  # Generates the spec as a Python dict (JSON compatible)
    # Converts dict to YAML string
    openapi_yaml = yaml.dump(openapi_spec, default_flow_style=False)
    return Response(content=openapi_yaml, media_type="application/x-yaml")
