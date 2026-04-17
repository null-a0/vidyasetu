from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_db, require_role
from app.config import settings
from app.core.redis import (
    get_job_progress,
    get_redis_async,
    job_dedup_lock_key,
    job_idempotency_key,
)
from app.crud.crud_ai_generation import (
    fail_stale_active_generations,
    find_active_generation_by_fingerprint,
    find_cached_completed_generation,
    get_ai_generation,
    list_ai_generations,
)
from app.models import AIFeatureType, AIGeneration, AIGenerationStatus, User, UserRole
from app.schemas.ai import (
    AdminAIReportCreateRequest,
    AdminAIReportCreateResponse,
    AdminAIReportListItem,
    AdminAIReportResultResponse,
    AdminAIReportStatusResponse,
)
from app.schemas.base import Page
from app.services.ai.admin_report_pipeline import (
    request_admin_report_generation,
)
from app.services.ai.cache import build_admin_report_request_fingerprint
from app.jobs.celery_app import celery_app
from app.services.ai.rate_limit import (
    DatabaseFixedWindowRateLimiter,
    InMemorySlidingWindowRateLimiter,
    RateLimitRule,
    RateLimitViolation,
    consume_rate_limit_or_raise,
)
from app.services.ai.validation import validate_admin_report_output
from app.crud.crud_rate_limit_events import create_rate_limit_event

router = APIRouter(prefix="/ai/reports", tags=["ai-reports"])


def _build_rate_limiter() -> InMemorySlidingWindowRateLimiter | DatabaseFixedWindowRateLimiter:
    backend = settings.AI_RATE_LIMIT_BACKEND.strip().lower()
    if backend == "memory":
        return InMemorySlidingWindowRateLimiter()
    if backend == "database":
        return DatabaseFixedWindowRateLimiter(
            retention_seconds=settings.AI_RATE_LIMIT_COUNTER_RETENTION_SECONDS,
        )
    raise ValueError("AI_RATE_LIMIT_BACKEND must be either 'database' or 'memory'.")


_rate_limiter = _build_rate_limiter()


def get_ai_rate_limiter() -> InMemorySlidingWindowRateLimiter | DatabaseFixedWindowRateLimiter:
    return _rate_limiter


def get_ai_rate_limit_rules() -> tuple[RateLimitRule, RateLimitRule]:
    return (
        RateLimitRule(
            max_requests=settings.AI_ADMIN_REPORT_USER_RATE_LIMIT,
            window_seconds=settings.AI_ADMIN_REPORT_RATE_LIMIT_WINDOW_SECONDS,
        ),
        RateLimitRule(
            max_requests=settings.AI_ADMIN_REPORT_INSTITUTION_RATE_LIMIT,
            window_seconds=settings.AI_ADMIN_REPORT_RATE_LIMIT_WINDOW_SECONDS,
        ),
    )


def _resolve_scope(
    payload: AdminAIReportCreateRequest,
    current_user: User,
) -> tuple[str | None, str, str]:
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if not current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Institution admin is not linked to any institution.",
            )
        if payload.institution_id and payload.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot generate reports outside your institution scope.",
            )
        return current_user.institution_id, "institution", current_user.institution_id

    if current_user.role == UserRole.ADMIN:
        if payload.institution_id:
            return payload.institution_id, "institution", payload.institution_id
        return None, "platform", "global"

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied.",
    )


def _assert_report_access(report: AIGeneration, current_user: User) -> None:
    if current_user.role == UserRole.ADMIN:
        return

    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if not current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Institution admin is not linked to any institution.",
            )
        if report.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this report scope.",
            )
        return

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")


@router.post(
    "/",
    response_model=AdminAIReportCreateResponse,
    summary="Create and generate an admin AI report",
)
async def create_admin_ai_report(
    payload: AdminAIReportCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
    limiter: InMemorySlidingWindowRateLimiter | DatabaseFixedWindowRateLimiter = Depends(get_ai_rate_limiter),
    rate_rules: tuple[RateLimitRule, RateLimitRule] = Depends(get_ai_rate_limit_rules),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> AdminAIReportCreateResponse:
    redis_client = get_redis_async()
    institution_id, source_entity_type, source_entity_id = _resolve_scope(payload, current_user)
    request_payload = payload.model_dump(mode="json")
    fingerprint_payload = {
        **request_payload,
        "institution_id": institution_id,
        "source_entity_type": source_entity_type,
        "source_entity_id": source_entity_id,
    }
    request_fingerprint = build_admin_report_request_fingerprint(
        institution_id=institution_id,
        source_entity_type=source_entity_type,
        source_entity_id=source_entity_id,
        prompt_version=settings.AI_ADMIN_REPORT_PROMPT_VERSION,
        model_name=settings.GEMINI_MODEL_NAME,
        raw_prompt_input=fingerprint_payload,
    )

    if idempotency_key:
        mapped = await redis_client.get(
            job_idempotency_key(
                user_id=current_user.id,
                route_key="POST:/ai/reports",
                key=idempotency_key,
            )
        )
        if mapped:
            existing = await get_ai_generation(db, str(mapped))
            if existing and existing.feature_type == AIFeatureType.ADMIN_REPORT:
                return AdminAIReportCreateResponse(
                    report_id=existing.id,
                    status=existing.status,
                    from_cache=False,
                    deduplicated=True,
                )

    lock_key = job_dedup_lock_key(fingerprint=request_fingerprint)
    got_lock = await redis_client.set(
        lock_key,
        current_user.id,
        nx=True,
        ex=settings.AI_JOB_DEDUP_LOCK_TTL_SECONDS,
    )
    await fail_stale_active_generations(
        db,
        feature_type=AIFeatureType.ADMIN_REPORT,
        stale_after_seconds=settings.AI_ADMIN_REPORT_STALE_AFTER_SECONDS,
    )

    if not payload.force_regenerate:
        if not got_lock:
            active = await find_active_generation_by_fingerprint(
                db,
                feature_type=AIFeatureType.ADMIN_REPORT,
                request_fingerprint=request_fingerprint,
            )
            if active:
                return AdminAIReportCreateResponse(
                    report_id=active.id,
                    status=active.status,
                    from_cache=False,
                    deduplicated=True,
                )

        active = await find_active_generation_by_fingerprint(
            db,
            feature_type=AIFeatureType.ADMIN_REPORT,
            request_fingerprint=request_fingerprint,
        )
        if active:
            return AdminAIReportCreateResponse(
                report_id=active.id,
                status=active.status,
                from_cache=False,
                deduplicated=True,
            )

        cached = await find_cached_completed_generation(
            db,
            feature_type=AIFeatureType.ADMIN_REPORT,
            request_fingerprint=request_fingerprint,
        )
        if cached:
            return AdminAIReportCreateResponse(
                report_id=cached.id,
                status=cached.status,
                from_cache=True,
                deduplicated=True,
            )

    user_rule, institution_rule = rate_rules
    institution_key = institution_id or "platform"
    try:
        await consume_rate_limit_or_raise(
            limiter=limiter,
            db=db,
            key=f"ai_report:user:{current_user.id}",
            rule=user_rule,
        )
    except RateLimitViolation as exc:
        await create_rate_limit_event(
            db,
            key=f"ai_report:user:{current_user.id}",
            allowed=False,
            remaining=exc.decision.remaining,
            retry_after_seconds=exc.decision.retry_after_seconds,
            rule_max_requests=user_rule.max_requests,
            rule_window_seconds=user_rule.window_seconds,
            actor_user_id=current_user.id,
            institution_id=institution_id,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded for report generation.",
            headers={"Retry-After": str(exc.decision.retry_after_seconds)},
        )

    try:
        await consume_rate_limit_or_raise(
            limiter=limiter,
            db=db,
            key=f"ai_report:institution:{institution_key}",
            rule=institution_rule,
        )
    except RateLimitViolation as exc:
        await create_rate_limit_event(
            db,
            key=f"ai_report:institution:{institution_key}",
            allowed=False,
            remaining=exc.decision.remaining,
            retry_after_seconds=exc.decision.retry_after_seconds,
            rule_max_requests=institution_rule.max_requests,
            rule_window_seconds=institution_rule.window_seconds,
            actor_user_id=current_user.id,
            institution_id=institution_id,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded for report generation.",
            headers={"Retry-After": str(exc.decision.retry_after_seconds)},
        )

    request_result = await request_admin_report_generation(
        db,
        requester_user_id=current_user.id,
        institution_id=institution_id,
        source_entity_type=source_entity_type,
        source_entity_id=source_entity_id,
        prompt_version=settings.AI_ADMIN_REPORT_PROMPT_VERSION,
        model_name=settings.GEMINI_MODEL_NAME,
        raw_prompt_input=fingerprint_payload,
        fingerprint_input=fingerprint_payload,
        cache_ttl_seconds=settings.AI_ADMIN_REPORT_CACHE_TTL_SECONDS,
        stale_after_seconds=settings.AI_ADMIN_REPORT_STALE_AFTER_SECONDS,
        force_regenerate=payload.force_regenerate,
    )
    generation = request_result.generation

    if idempotency_key:
        await redis_client.set(
            job_idempotency_key(
                user_id=current_user.id,
                route_key="POST:/ai/reports",
                key=idempotency_key,
            ),
            generation.id,
            ex=settings.AI_JOB_IDEMPOTENCY_TTL_SECONDS,
        )

    if generation.status in (AIGenerationStatus.PENDING, AIGenerationStatus.PROCESSING):
        celery_app.send_task(
            "app.jobs.tasks.generate_admin_ai_report",
            kwargs={"generation_id": generation.id},
            queue=settings.CELERY_TASK_DEFAULT_QUEUE,
        )

    return AdminAIReportCreateResponse(
        report_id=generation.id,
        status=generation.status,
        from_cache=request_result.from_cache,
        deduplicated=request_result.deduplicated,
    )


@router.get(
    "/{report_id}/status",
    response_model=AdminAIReportStatusResponse,
    summary="Get admin AI report generation status",
)
async def get_admin_ai_report_status(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> AdminAIReportStatusResponse:
    report = await get_ai_generation(db, report_id)
    if not report or report.feature_type != AIFeatureType.ADMIN_REPORT:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    _assert_report_access(report, current_user)
    progress = None
    try:
        progress_obj = await get_job_progress(get_redis_async(), generation_id=report.id)
        progress = progress_obj.__dict__ if progress_obj else None
    except Exception:
        progress = None
    return AdminAIReportStatusResponse(
        report_id=report.id,
        status=report.status,
        error_details=report.error_details,
        progress=progress,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


@router.get(
    "/{report_id}/result",
    response_model=AdminAIReportResultResponse,
    summary="Get completed admin AI report result",
)
async def get_admin_ai_report_result(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> AdminAIReportResultResponse:
    report = await get_ai_generation(db, report_id)
    if not report or report.feature_type != AIFeatureType.ADMIN_REPORT:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    _assert_report_access(report, current_user)

    if report.status != AIGenerationStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Report is not completed yet.",
        )
    if not isinstance(report.parsed_output_json, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored report output is invalid.",
        )

    validated = validate_admin_report_output(report.parsed_output_json)
    return AdminAIReportResultResponse(
        report_id=report.id,
        status=report.status,
        result=validated,
        created_at=report.created_at,
        updated_at=report.updated_at,
        prompt_version=report.prompt_version,
        model_name=report.model_name,
    )


@router.get(
    "/",
    response_model=Page[AdminAIReportListItem],
    summary="List previous admin AI reports",
)
async def list_admin_ai_reports(
    page: PaginationParams = Depends(),
    institution_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> Page[AdminAIReportListItem]:
    scoped_institution_id = institution_id
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if not current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Institution admin is not linked to any institution.",
            )
        if scoped_institution_id and scoped_institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot list reports outside your institution scope.",
            )
        scoped_institution_id = current_user.institution_id

    rows, total = await list_ai_generations(
        db,
        feature_type=AIFeatureType.ADMIN_REPORT,
        institution_id=scoped_institution_id,
        offset=page.offset,
        limit=page.limit,
    )
    items = [
        AdminAIReportListItem(
            report_id=row.id,
            status=row.status,
            institution_id=row.institution_id,
            source_entity_type=row.source_entity_type,
            source_entity_id=row.source_entity_id,
            prompt_version=row.prompt_version,
            model_name=row.model_name,
            summary_preview=(row.parsed_output_json or {}).get("summary")
            if isinstance(row.parsed_output_json, dict)
            else None,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]
    return Page(items=items, total=total, offset=page.offset, limit=page.limit)
