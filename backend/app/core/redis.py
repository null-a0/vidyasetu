from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

import redis
import redis.asyncio as aioredis

from app.config import settings


def _require_redis_url() -> str:
    url = settings.REDIS_URL.strip()
    if not url:
        raise RuntimeError("REDIS_URL must be configured for async AI jobs.")
    return url


def get_redis_sync() -> redis.Redis:
    return redis.Redis.from_url(_require_redis_url(), decode_responses=True)


def get_redis_async() -> aioredis.Redis:
    return aioredis.Redis.from_url(_require_redis_url(), decode_responses=True)


@dataclass(frozen=True)
class JobProgress:
    state: str
    percent: int | None = None
    message: str | None = None
    updated_at: str | None = None

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()


def job_progress_key(*, generation_id: str) -> str:
    return f"job:ai_generation:{generation_id}:progress"


def job_dedup_lock_key(*, fingerprint: str) -> str:
    return f"lock:ai_generation:fingerprint:{fingerprint}"


def job_idempotency_key(*, user_id: str, route_key: str, key: str) -> str:
    safe_route = route_key.replace(":", "_").replace("/", "_")
    return f"idempotency:{user_id}:{safe_route}:{key}"


def _json_dumps(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


async def set_job_progress(
    redis_client: aioredis.Redis,
    *,
    generation_id: str,
    state: str,
    percent: int | None = None,
    message: str | None = None,
    ttl_seconds: int | None = None,
) -> None:
    progress = JobProgress(
        state=state,
        percent=percent,
        message=message,
        updated_at=JobProgress.now_iso(),
    )
    ttl_seconds = ttl_seconds or settings.AI_JOB_PROGRESS_TTL_SECONDS
    await redis_client.set(
        job_progress_key(generation_id=generation_id),
        _json_dumps(asdict(progress)),
        ex=ttl_seconds,
    )


async def get_job_progress(
    redis_client: aioredis.Redis,
    *,
    generation_id: str,
) -> JobProgress | None:
    raw = await redis_client.get(job_progress_key(generation_id=generation_id))
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return JobProgress(
        state=str(payload.get("state") or ""),
        percent=payload.get("percent"),
        message=payload.get("message"),
        updated_at=payload.get("updated_at"),
    )

