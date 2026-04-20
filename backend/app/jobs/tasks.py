from __future__ import annotations

import asyncio
import json
import logging
import random
from datetime import date, datetime, timezone, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.redis import get_redis_async, set_job_progress
from app.crud.crud_ai_generation import get_ai_generation, update_ai_generation
from app.crud.crud_misc import create_notification
from app.db import AsyncSessionLocal
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
from app.services.sanitize import sanitize_text

logger = logging.getLogger(__name__)

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

async def _dead_letter(*, redis_client: Any, generation_id: str, payload: dict[str, Any]) -> None:
    try:
        await redis_client.lpush(
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
    except Exception:
        pass

def _retry_backoff_seconds(retry_number: int) -> int:
    base = min(60 * 10, int((2**retry_number) * 2))
    jitter = random.randint(0, max(1, base // 4))
    return base + jitter

async def _with_session(fn):
    async with AsyncSessionLocal() as session:
        try:
            result = await fn(session)
            await session.commit()
            return result
        except Exception:
            await session.rollback()
            raise
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

async def _run_admin_report_attempt(db: AsyncSession, redis_client: Any, generation_id: str, scheduled_run_id: str | None) -> None:
    generation = await get_ai_generation(db, generation_id)
    if not generation or generation.feature_type != AIFeatureType.ADMIN_REPORT:
        return
    if generation.status == AIGenerationStatus.COMPLETED:
        return

    await set_job_progress(
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
        await set_job_progress(
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

        await set_job_progress(
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

        await set_job_progress(
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

        await set_job_progress(
            redis_client=redis_client,
            generation_id=generation_id,
            state="validate",
            percent=80,
            message="Validating model output",
        )
        validated = validate_admin_report_output(result.parsed_output)

        await set_job_progress(
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

        await set_job_progress(
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

async def generate_admin_ai_report(generation_id: str, *, scheduled_run_id: str | None = None) -> None:
    redis_client = get_redis_async()
    retries = 0
    while True:
        try:
            await _with_session(lambda db: _run_admin_report_attempt(db, redis_client, generation_id, scheduled_run_id))
            break
        except GeminiTransientError as exc:
            retries += 1
            if retries > settings.AI_JOB_MAX_RETRIES:
                await _dead_letter(
                    redis_client=redis_client,
                    generation_id=generation_id,
                    payload={"task": "generate_admin_ai_report", "error": str(exc)},
                )
                await set_job_progress(redis_client=redis_client, generation_id=generation_id, state="failed", percent=None, message=f"Max retries exceeded: {exc}")
                logger.error(f"AI job failed after max retries: {exc}")
                break
            countdown = _retry_backoff_seconds(retries)
            await set_job_progress(
                redis_client=redis_client,
                generation_id=generation_id,
                state="retrying",
                percent=None,
                message=f"Transient error, retrying in {countdown}s (attempt {retries}).",
            )
            await asyncio.sleep(countdown)
        except Exception as exc:
            await set_job_progress(redis_client=redis_client, generation_id=generation_id, state="failed", percent=None, message=str(exc))
            logger.error(f"AI job failed: {exc}")
            break

async def _run_student_explanation_attempt(db: AsyncSession, redis_client: Any, generation_id: str) -> None:
    generation = await get_ai_generation(db, generation_id)
    if not generation or generation.feature_type != AIFeatureType.STUDENT_EXPLANATION:
        return
    if generation.status == AIGenerationStatus.COMPLETED:
        return

    await set_job_progress(
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

        await set_job_progress(
            redis_client=redis_client,
            generation_id=generation_id,
            state="prompt",
            percent=20,
            message="Compiling prompt",
        )
        prompt = build_student_explanation_prompt(prompt_payload=prompt_payload)

        await set_job_progress(
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

        await set_job_progress(
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

        await set_job_progress(
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

        await set_job_progress(
            redis_client=redis_client,
            generation_id=generation_id,
            state="done",
            percent=100,
            message="Explanation ready",
        )

    except Exception as exc:
        await _mark_failed(db, generation=generation, error=exc)
        raise

async def generate_student_explanation(generation_id: str) -> None:
    redis_client = get_redis_async()
    retries = 0
    while True:
        try:
            await _with_session(lambda db: _run_student_explanation_attempt(db, redis_client, generation_id))
            break
        except GeminiTransientError as exc:
            retries += 1
            if retries > settings.AI_JOB_MAX_RETRIES:
                await _dead_letter(
                    redis_client=redis_client,
                    generation_id=generation_id,
                    payload={"task": "generate_student_explanation", "error": str(exc)},
                )
                await set_job_progress(redis_client=redis_client, generation_id=generation_id, state="failed", percent=None, message=f"Max retries exceeded: {exc}")
                logger.error(f"Student explanation job failed after max retries: {exc}")
                break
            countdown = _retry_backoff_seconds(retries)
            await set_job_progress(
                redis_client=redis_client,
                generation_id=generation_id,
                state="retrying",
                percent=None,
                message=f"Transient error, retrying in {countdown}s (attempt {retries}).",
            )
            await asyncio.sleep(countdown)
        except Exception as exc:
            await set_job_progress(redis_client=redis_client, generation_id=generation_id, state="failed", percent=None, message=str(exc))
            logger.error(f"Student explanation job failed: {exc}")
            break

async def _run_tick_scheduled_reports(db: AsyncSession) -> None:
    from app.crud.crud_scheduled_reports import (
        find_due_scheduled_reports,
        mark_scheduled_run_processing,
    )
    from app.services.ai.admin_report_pipeline import request_admin_report_generation

    due_runs = await find_due_scheduled_reports(
        db, target_time=_utc_now() + timedelta(seconds=settings.SCHEDULED_REPORT_LOOKAHEAD_SECONDS)
    )
    if not due_runs:
        return

    for run_info in due_runs:
        report, next_run = run_info.report, run_info.next_run
        scheduled_run = await mark_scheduled_run_processing(db, report=report, run_date=next_run)
        if not scheduled_run:
            continue

        try:
            req_result = await request_admin_report_generation(
                db,
                institution_id=report.institution_id,
                requester_user_id=report.created_by,
                source_entity_type="scheduled_report",
                source_entity_id=report.id,
                focus_areas=report.focus_areas,
                date_from=None,
                date_to=None,
                force_regenerate=True,
                bypass_rate_limits=True,
            )
            asyncio.create_task(generate_admin_ai_report(req_result.generation.id, scheduled_run_id=scheduled_run.id))
        except Exception as exc:
            logger.exception("Failed to enqueue scheduled report generation %s", report.id)
            try:
                from app.crud.crud_scheduled_reports import mark_scheduled_run_failed
                await mark_scheduled_run_failed(
                    db, run_id=scheduled_run.id, error_details={"error_type": exc.__class__.__name__, "message": str(exc)}
                )
            except Exception:
                pass

async def tick_scheduled_ai_reports() -> None:
    try:
        await _with_session(_run_tick_scheduled_reports)
    except Exception as exc:
        logger.exception("Failed tick_scheduled_ai_reports task %s", exc)
