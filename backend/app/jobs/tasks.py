from __future__ import annotations

import asyncio
import json
import random
from datetime import date, datetime, timezone
from typing import Any

from celery import Task
from celery.utils.log import get_task_logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.redis import job_progress_key
from app.crud.crud_ai_generation import get_ai_generation, update_ai_generation
from app.crud.crud_misc import create_notification
from app.db import AsyncSessionLocal
from app.jobs.celery_app import celery_app
from app.models import (
    AIFeatureType,
    AIGeneration,
    AIGenerationStatus,
    NotificationType,
)
from app.schemas.ai import (
    ADMIN_REPORT_RESPONSE_JSON_SCHEMA,
    STUDENT_EXPLANATION_RESPONSE_JSON_SCHEMA,
    AIGenerationUpdate,
    AITokenUsage,
)
from app.schemas.misc import NotificationCreate
from app.services.ai.admin_report_context import build_admin_report_context
from app.services.ai.admin_report_prompt import build_admin_report_prompt
from app.services.ai.cache import compute_cache_expiry
from app.services.ai.gemini_client import GeminiClient, GeminiTransientError
from app.services.ai.student_explanation_prompt import build_student_explanation_prompt
from app.services.ai.validation import (
    validate_admin_report_output,
    validate_student_explanation_output,
)

logger = get_task_logger(__name__)


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _progress_set(*, redis_client: Any, generation_id: str, state: str, percent: int | None, message: str | None) -> None:
    payload = {
        "state": state,
        "percent": percent,
        "message": message,
        "updated_at": _utc_now().isoformat(),
    }
    redis_client.set(
        job_progress_key(generation_id=generation_id),
        json.dumps(payload, ensure_ascii=True, sort_keys=True),
        ex=settings.AI_JOB_PROGRESS_TTL_SECONDS,
    )


def _dead_letter(*, redis_client: Any, generation_id: str, payload: dict[str, Any]) -> None:
    redis_client.lpush(
        "dlq:ai_generations",
        json.dumps(
            {
                "generation_id": generation_id,
                "payload": payload,
                "dead_lettered_at": _utc_now().isoformat(),
            },
            ensure_ascii=True,
            sort_keys=True,
        ),
    )


def _retry_backoff_seconds(retry_number: int) -> int:
    base = min(60 * 10, int((2**retry_number) * 2))
    jitter = random.randint(0, max(1, base // 4))
    return base + jitter


async def _with_session(fn):
    async with AsyncSessionLocal() as session:
        try:
            return await fn(session)
        finally:
            await session.close()


async def _mark_failed(
    db: AsyncSession,
    *,
    generation: AIGeneration | None,
    error: Exception,
) -> None:
    if not generation:
        return
    try:
        await update_ai_generation(
            db,
            generation,
            AIGenerationUpdate(
                status=AIGenerationStatus.FAILED,
                error_details={
                    "error_type": error.__class__.__name__,
                    "message": str(error),
                },
            ),
        )
    except Exception:
        return


class AIJobTask(Task):
    autoretry_for = ()
    retry_backoff = False
    retry_jitter = False

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        try:
            from app.core.redis import get_redis_sync
            from app.services.sanitize import sanitize_text

            redis_client = get_redis_sync()
            generation_id = kwargs.get("generation_id") or (args[0] if args else None)
            if isinstance(generation_id, str) and generation_id:
                _progress_set(
                    redis_client=redis_client,
                    generation_id=generation_id,
                    state="failed",
                    percent=None,
                    message=str(exc),
                )
                trace = ""
                try:
                    trace = getattr(einfo, "traceback", "") or ""
                except Exception:
                    trace = ""
                if trace:
                    redis_client.set(
                        f"trace:ai_generation:{generation_id}",
                        sanitize_text(str(trace)),
                        ex=settings.AI_JOB_PROGRESS_TTL_SECONDS,
                    )
        except Exception:
            pass
        super().on_failure(exc, task_id, args, kwargs, einfo)


@celery_app.task(name="app.jobs.tasks.generate_admin_ai_report", bind=True, base=AIJobTask)
def generate_admin_ai_report(self: AIJobTask, generation_id: str, *, scheduled_run_id: str | None = None) -> None:
    from app.core.redis import get_redis_sync

    redis_client = get_redis_sync()

    async def _run(db: AsyncSession) -> None:
        generation = await get_ai_generation(db, generation_id)
        if not generation or generation.feature_type != AIFeatureType.ADMIN_REPORT:
            return
        if generation.status == AIGenerationStatus.COMPLETED:
            return

        _progress_set(
            redis_client=redis_client,
            generation_id=generation_id,
            state="starting",
            percent=1,
            message="Starting report job",
        )
        await update_ai_generation(db, generation, AIGenerationUpdate(status=AIGenerationStatus.PROCESSING))

        request_payload = generation.raw_prompt_input or {}
        date_from = _parse_date(request_payload.get("date_from"))
        date_to = _parse_date(request_payload.get("date_to"))

        try:
            _progress_set(
                redis_client=redis_client,
                generation_id=generation_id,
                state="context",
                percent=10,
                message="Building analytics context",
            )
            context = await build_admin_report_context(
                db,
                institution_id=generation.institution_id,
                date_from=date_from,
                date_to=date_to,
            )

            _progress_set(
                redis_client=redis_client,
                generation_id=generation_id,
                state="prompt",
                percent=25,
                message="Compiling prompt",
            )
            compiled_prompt = build_admin_report_prompt(
                request_payload=request_payload,
                analytics_context=context,
            )

            _progress_set(
                redis_client=redis_client,
                generation_id=generation_id,
                state="model",
                percent=45,
                message="Calling Gemini",
            )
            gemini = GeminiClient.from_settings()
            result = await gemini.generate_structured(
                prompt=compiled_prompt,
                response_json_schema=ADMIN_REPORT_RESPONSE_JSON_SCHEMA,
            )

            _progress_set(
                redis_client=redis_client,
                generation_id=generation_id,
                state="validate",
                percent=80,
                message="Validating model output",
            )
            validated = validate_admin_report_output(result.parsed_output)

            _progress_set(
                redis_client=redis_client,
                generation_id=generation_id,
                state="persist",
                percent=90,
                message="Persisting result",
            )
            await update_ai_generation(
                db,
                generation,
                AIGenerationUpdate(
                    status=AIGenerationStatus.COMPLETED,
                    raw_model_output=result.raw_output,
                    parsed_output_json=validated.model_dump(),
                    error_details={},
                    retry_count=result.retries_used,
                    token_usage=AITokenUsage(
                        input_tokens=result.usage.input_tokens,
                        output_tokens=result.usage.output_tokens,
                        total_tokens=result.usage.total_tokens,
                    ),
                    cache_expires_at=compute_cache_expiry(ttl_seconds=settings.AI_ADMIN_REPORT_CACHE_TTL_SECONDS),
                ),
            )

            _progress_set(
                redis_client=redis_client,
                generation_id=generation_id,
                state="done",
                percent=100,
                message="Report ready",
            )

            if scheduled_run_id:
                try:
                    from app.crud.crud_scheduled_reports import mark_scheduled_run_completed

                    await mark_scheduled_run_completed(db, run_id=scheduled_run_id, generation_id=generation_id)
                except Exception as exc:
                    logger.warning("Failed to finalize scheduled run %s: %s", scheduled_run_id, exc)

            try:
                await create_notification(
                    db,
                    NotificationCreate(
                        user_id=generation.requester_user_id,
                        message=f"AI report is ready (id: {generation_id}).",
                        notification_type=NotificationType.GENERAL,
                    ),
                )
            except Exception:
                pass
        except Exception as exc:
            await _mark_failed(db, generation=generation, error=exc)
            if scheduled_run_id:
                try:
                    from app.crud.crud_scheduled_reports import mark_scheduled_run_failed

                    await mark_scheduled_run_failed(
                        db,
                        run_id=scheduled_run_id,
                        error_details={"error_type": exc.__class__.__name__, "message": str(exc)},
                    )
                except Exception:
                    pass
            raise

    try:
        asyncio.run(_with_session(_run))
    except GeminiTransientError as exc:
        retry_number = int(getattr(self.request, "retries", 0) or 0) + 1
        if retry_number > settings.AI_JOB_MAX_RETRIES:
            _dead_letter(
                redis_client=redis_client,
                generation_id=generation_id,
                payload={"task": "generate_admin_ai_report", "error": str(exc)},
            )
            raise
        countdown = _retry_backoff_seconds(retry_number)
        _progress_set(
            redis_client=redis_client,
            generation_id=generation_id,
            state="retrying",
            percent=None,
            message=f"Transient error, retrying in {countdown}s (attempt {retry_number}).",
        )
        raise self.retry(exc=exc, countdown=countdown, max_retries=settings.AI_JOB_MAX_RETRIES)


@celery_app.task(name="app.jobs.tasks.generate_student_explanation", bind=True, base=AIJobTask)
def generate_student_explanation(self: AIJobTask, generation_id: str) -> None:
    from app.core.redis import get_redis_sync

    redis_client = get_redis_sync()

    async def _run(db: AsyncSession) -> None:
        generation = await get_ai_generation(db, generation_id)
        if not generation or generation.feature_type != AIFeatureType.STUDENT_EXPLANATION:
            return
        if generation.status == AIGenerationStatus.COMPLETED:
            return

        _progress_set(
            redis_client=redis_client,
            generation_id=generation_id,
            state="starting",
            percent=1,
            message="Starting explanation job",
        )
        await update_ai_generation(db, generation, AIGenerationUpdate(status=AIGenerationStatus.PROCESSING))

        try:
            raw = generation.raw_prompt_input or {}
            prompt_payload = raw.get("prompt_payload") if isinstance(raw, dict) else None
            if not isinstance(prompt_payload, dict):
                prompt_payload = {}
            disallowed_option_ids = (raw.get("correct_option_ids") if isinstance(raw, dict) else None) or []
            disallowed_option_texts = (raw.get("correct_option_texts") if isinstance(raw, dict) else None) or []
            if not isinstance(disallowed_option_ids, list):
                disallowed_option_ids = []
            if not isinstance(disallowed_option_texts, list):
                disallowed_option_texts = []
            disallowed_option_ids = [str(v) for v in disallowed_option_ids if v]
            disallowed_option_texts = [str(v) for v in disallowed_option_texts if v]

            _progress_set(
                redis_client=redis_client,
                generation_id=generation_id,
                state="prompt",
                percent=20,
                message="Compiling prompt",
            )
            prompt = build_student_explanation_prompt(prompt_payload=prompt_payload)

            _progress_set(
                redis_client=redis_client,
                generation_id=generation_id,
                state="model",
                percent=45,
                message="Calling Gemini",
            )
            gemini = GeminiClient.from_settings()
            result = await gemini.generate_structured(
                prompt=prompt,
                response_json_schema=STUDENT_EXPLANATION_RESPONSE_JSON_SCHEMA,
            )

            _progress_set(
                redis_client=redis_client,
                generation_id=generation_id,
                state="validate",
                percent=80,
                message="Validating model output",
            )
            validated = validate_student_explanation_output(
                result.parsed_output,
                disallowed_option_ids=disallowed_option_ids,
                disallowed_option_texts=disallowed_option_texts,
            )

            _progress_set(
                redis_client=redis_client,
                generation_id=generation_id,
                state="persist",
                percent=90,
                message="Persisting result",
            )
            await update_ai_generation(
                db,
                generation,
                AIGenerationUpdate(
                    status=AIGenerationStatus.COMPLETED,
                    raw_model_output=result.raw_output,
                    parsed_output_json=validated.model_dump(),
                    error_details={},
                    retry_count=result.retries_used,
                    token_usage=AITokenUsage(
                        input_tokens=result.usage.input_tokens,
                        output_tokens=result.usage.output_tokens,
                        total_tokens=result.usage.total_tokens,
                    ),
                    cache_expires_at=compute_cache_expiry(ttl_seconds=settings.AI_STUDENT_EXPLANATION_CACHE_TTL_SECONDS),
                ),
            )

            _progress_set(
                redis_client=redis_client,
                generation_id=generation_id,
                state="done",
                percent=100,
                message="Explanation ready",
            )
        except Exception as exc:
            await _mark_failed(db, generation=generation, error=exc)
            raise

    try:
        asyncio.run(_with_session(_run))
    except GeminiTransientError as exc:
        retry_number = int(getattr(self.request, "retries", 0) or 0) + 1
        if retry_number > settings.AI_JOB_MAX_RETRIES:
            _dead_letter(
                redis_client=redis_client,
                generation_id=generation_id,
                payload={"task": "generate_student_explanation", "error": str(exc)},
            )
            raise
        countdown = _retry_backoff_seconds(retry_number)
        _progress_set(
            redis_client=redis_client,
            generation_id=generation_id,
            state="retrying",
            percent=None,
            message=f"Transient error, retrying in {countdown}s (attempt {retry_number}).",
        )
        raise self.retry(exc=exc, countdown=countdown, max_retries=settings.AI_JOB_MAX_RETRIES)


@celery_app.task(name="app.jobs.tasks.tick_scheduled_ai_reports")
def tick_scheduled_ai_reports() -> None:
    async def _run(db: AsyncSession) -> None:
        from app.crud.crud_scheduled_reports import claim_due_scheduled_runs

        rows = await claim_due_scheduled_runs(
            db,
            now=_utc_now(),
            lookahead_seconds=settings.SCHEDULED_REPORT_LOOKAHEAD_SECONDS,
        )
        if not rows:
            return

        for run in rows:
            celery_app.send_task(
                "app.jobs.tasks.generate_admin_ai_report",
                kwargs={"generation_id": run.ai_generation_id, "scheduled_run_id": run.id},
                queue=settings.CELERY_TASK_DEFAULT_QUEUE,
            )

    asyncio.run(_with_session(_run))
