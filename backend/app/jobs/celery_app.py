from __future__ import annotations

import ssl

from celery import Celery

from app.config import settings


def _redis_ssl_options(url: str) -> dict[str, object]:
    if not url.startswith("rediss://"):
        return {}
    context = ssl.create_default_context()
    return {
        "ssl": context,
        "ssl_cert_reqs": ssl.CERT_REQUIRED,
    }


celery_app = Celery(
    "vidyasetu",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.jobs.tasks"],
)

celery_app.conf.update(
    task_default_queue=settings.CELERY_TASK_DEFAULT_QUEUE,
    broker_transport_options={
        **_redis_ssl_options(settings.celery_broker_url),
        "visibility_timeout": 60 * 60,
    },
    redis_backend_transport_options=_redis_ssl_options(settings.celery_result_backend),
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_time_limit=60 * 10,
    task_soft_time_limit=60 * 9,
)

celery_app.conf.beat_schedule = {
    "tick_scheduled_ai_reports": {
        "task": "app.jobs.tasks.tick_scheduled_ai_reports",
        "schedule": 60.0,
    }
}
