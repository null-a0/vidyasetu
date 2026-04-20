from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.config import settings
from app.core.redis import get_job_progress, get_redis_async, job_dedup_lock_key, job_idempotency_key
from app.crud.crud_ai_generation import (
    create_ai_generation,
    fail_stale_active_generations,
    find_active_generation_by_fingerprint,
    find_cached_completed_generation,
    get_ai_generation,
)
from app.crud.crud_assessment import get_question, get_submission
from app.jobs.tasks import generate_student_explanation
from app.models import AIFeatureType, AIGenerationStatus, User, UserRole
from app.schemas.ai import (
    AIGenerationCreate,
    StudentExplanationCreateRequest,
    StudentExplanationCreateResponse,
    StudentExplanationResultResponse,
    StudentExplanationStatusResponse,
)
from app.services.ai.cache import (
    build_student_explanation_request_fingerprint,
    compute_cache_expiry,
)
from app.services.ai.rate_limit import (
    DatabaseFixedWindowRateLimiter,
    InMemorySlidingWindowRateLimiter,
    RateLimitRule,
    RateLimitViolation,
    consume_rate_limit_or_raise,
)
from app.services.ai.validation import validate_student_explanation_output
from app.crud.crud_rate_limit_events import create_rate_limit_event

router = APIRouter(prefix="/ai/student-explanations", tags=["ai-student-explanations"])


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


def get_student_explanation_rate_limiter() -> InMemorySlidingWindowRateLimiter | DatabaseFixedWindowRateLimiter:
    return _rate_limiter


def get_student_explanation_rate_limit_rule() -> RateLimitRule:
    return RateLimitRule(
        max_requests=settings.AI_STUDENT_EXPLANATION_USER_RATE_LIMIT,
        window_seconds=settings.AI_STUDENT_EXPLANATION_RATE_LIMIT_WINDOW_SECONDS,
    )


@router.post(
    "/",
    response_model=StudentExplanationCreateResponse,
    summary="Generate student-facing explanation for an incorrect answer",
)
async def create_student_explanation(
    payload: StudentExplanationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    limiter: InMemorySlidingWindowRateLimiter | DatabaseFixedWindowRateLimiter = Depends(
        get_student_explanation_rate_limiter
    ),
    rate_rule: RateLimitRule = Depends(get_student_explanation_rate_limit_rule),
    background_tasks: BackgroundTasks = None,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> StudentExplanationCreateResponse:
    redis_client = get_redis_async()
    submission = await get_submission(db, payload.submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")
    if submission.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    if submission.pass_fail is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Submission is not graded yet.",
        )

    question = await get_question(db, payload.question_id)
    if not question or question.assessment_id != submission.assessment_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found in this submission.")

    answers = submission.answers or []
    answer_row = next(
        (
            item
            for item in answers
            if isinstance(item, dict) and item.get("question_id") == payload.question_id
        ),
        None,
    )
    selected_option_ids = (
        answer_row.get("selected_option_ids", [])
        if isinstance(answer_row, dict)
        else []
    )
    if not isinstance(selected_option_ids, list):
        selected_option_ids = []
    selected_option_ids = [str(value) for value in selected_option_ids if value]
    if not selected_option_ids:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Question has no submitted answer for explanation.",
        )

    options = question.options or []
    option_lookup = {
        str(item.get("id")): str(item.get("text", ""))
        for item in options
        if isinstance(item, dict) and item.get("id")
    }
    correct_option_ids = [
        str(item.get("id"))
        for item in options
        if isinstance(item, dict) and item.get("id") and item.get("is_correct")
    ]
    selected_option_texts = [option_lookup.get(option_id, "") for option_id in selected_option_ids]
    correct_option_texts = [option_lookup.get(option_id, "") for option_id in correct_option_ids]

    if sorted(selected_option_ids) == sorted(correct_option_ids):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Explanation is available only for incorrect answers.",
        )

    prompt_payload_for_model = {
        "question_id": question.id,
        "question_text": question.text or "",
        "question_type": question.type.value if hasattr(question.type, "value") else str(question.type or ""),
        "student_selected_option_texts": selected_option_texts,
        "student_selected_option_ids": selected_option_ids,
        "correct_option_texts_internal_only": correct_option_texts,
    }
    raw_prompt_input = {
        "prompt_payload": prompt_payload_for_model,
        "correct_option_ids": correct_option_ids,
        "correct_option_texts": correct_option_texts,
    }
    request_fingerprint = build_student_explanation_request_fingerprint(
        student_id=current_user.id,
        submission_id=submission.id,
        question_id=question.id,
        prompt_version=settings.AI_STUDENT_EXPLANATION_PROMPT_VERSION,
        model_name=settings.GEMINI_MODEL_NAME,
        raw_prompt_input=raw_prompt_input,
    )

    if idempotency_key:
        mapped = await redis_client.get(
            job_idempotency_key(
                user_id=current_user.id,
                route_key="POST:/ai/student-explanations",
                key=idempotency_key,
            )
        )
        if mapped:
            existing = await get_ai_generation(db, str(mapped))
            if existing and existing.feature_type == AIFeatureType.STUDENT_EXPLANATION:
                return StudentExplanationCreateResponse(
                    explanation_id=existing.id,
                    status=existing.status,
                    from_cache=False,
                    explanation=None,
                )

    await fail_stale_active_generations(
        db,
        feature_type=AIFeatureType.STUDENT_EXPLANATION,
        stale_after_seconds=settings.AI_STUDENT_EXPLANATION_STALE_AFTER_SECONDS,
        request_fingerprint=request_fingerprint,
    )

    if not payload.force_regenerate:
        active = await find_active_generation_by_fingerprint(
            db,
            feature_type=AIFeatureType.STUDENT_EXPLANATION,
            request_fingerprint=request_fingerprint,
        )
        if active:
            return StudentExplanationCreateResponse(
                explanation_id=active.id,
                status=active.status,
                from_cache=False,
                explanation=None,
            )

        cached = await find_cached_completed_generation(
            db,
            feature_type=AIFeatureType.STUDENT_EXPLANATION,
            request_fingerprint=request_fingerprint,
        )
        if cached and isinstance(cached.parsed_output_json, dict):
            validated_cached = validate_student_explanation_output(
                cached.parsed_output_json,
                disallowed_option_ids=correct_option_ids,
                disallowed_option_texts=correct_option_texts,
            )
            return StudentExplanationCreateResponse(
                explanation_id=cached.id,
                status=cached.status,
                from_cache=True,
                explanation=validated_cached,
            )

    try:
        await consume_rate_limit_or_raise(
            limiter=limiter,
            db=db,
            key=f"ai_student_explanation:user:{current_user.id}",
            rule=rate_rule,
        )
    except RateLimitViolation as exc:
        await create_rate_limit_event(
            db,
            key=f"ai_student_explanation:user:{current_user.id}",
            allowed=False,
            remaining=exc.decision.remaining,
            retry_after_seconds=exc.decision.retry_after_seconds,
            rule_max_requests=rate_rule.max_requests,
            rule_window_seconds=rate_rule.window_seconds,
            actor_user_id=current_user.id,
            institution_id=current_user.institution_id,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded for student explanations.",
            headers={"Retry-After": str(exc.decision.retry_after_seconds)},
        )

    generation = await create_ai_generation(
        db,
        AIGenerationCreate(
            feature_type=AIFeatureType.STUDENT_EXPLANATION,
            requester_user_id=current_user.id,
            institution_id=current_user.institution_id,
            source_entity_type="submission_question",
            source_entity_id=f"{submission.id}:{question.id}",
            prompt_version=settings.AI_STUDENT_EXPLANATION_PROMPT_VERSION,
            model_name=settings.GEMINI_MODEL_NAME,
            raw_prompt_input=raw_prompt_input,
            request_fingerprint=request_fingerprint,
            cache_expires_at=compute_cache_expiry(
                ttl_seconds=settings.AI_STUDENT_EXPLANATION_CACHE_TTL_SECONDS
            ),
        ),
    )

    if idempotency_key:
        await redis_client.set(
            job_idempotency_key(
                user_id=current_user.id,
                route_key="POST:/ai/student-explanations",
                key=idempotency_key,
            ),
            generation.id,
            ex=settings.AI_JOB_IDEMPOTENCY_TTL_SECONDS,
        )

    await redis_client.set(
        job_dedup_lock_key(fingerprint=request_fingerprint),
        current_user.id,
        nx=True,
        ex=settings.AI_JOB_DEDUP_LOCK_TTL_SECONDS,
    )

    background_tasks.add_task(generate_student_explanation, generation_id=generation.id)

    return StudentExplanationCreateResponse(
        explanation_id=generation.id,
        status=generation.status,
        from_cache=False,
        explanation=None,
    )


@router.get(
    "/{explanation_id}/status",
    response_model=StudentExplanationStatusResponse,
    summary="Get student explanation generation status",
)
async def get_student_explanation_status(
    explanation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
) -> StudentExplanationStatusResponse:
    row = await get_ai_generation(db, explanation_id)
    if not row or row.feature_type != AIFeatureType.STUDENT_EXPLANATION:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Explanation not found.")
    if row.requester_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    progress = None
    try:
        progress_obj = await get_job_progress(get_redis_async(), generation_id=row.id)
        progress = progress_obj.__dict__ if progress_obj else None
    except Exception:
        progress = None

    return StudentExplanationStatusResponse(
        explanation_id=row.id,
        status=row.status,
        error_details=row.error_details,
        progress=progress,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get(
    "/{explanation_id}/result",
    response_model=StudentExplanationResultResponse,
    summary="Get completed student explanation result",
)
async def get_student_explanation_result(
    explanation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
) -> StudentExplanationResultResponse:
    row = await get_ai_generation(db, explanation_id)
    if not row or row.feature_type != AIFeatureType.STUDENT_EXPLANATION:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Explanation not found.")
    if row.requester_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if row.status != AIGenerationStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Explanation is not completed yet.")
    if not isinstance(row.parsed_output_json, dict):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Stored explanation output is invalid.")

    raw = row.raw_prompt_input or {}
    disallowed_option_ids = raw.get("correct_option_ids") or []
    disallowed_option_texts = raw.get("correct_option_texts") or []
    if not isinstance(disallowed_option_ids, list):
        disallowed_option_ids = []
    if not isinstance(disallowed_option_texts, list):
        disallowed_option_texts = []

    validated = validate_student_explanation_output(
        row.parsed_output_json,
        disallowed_option_ids=[str(v) for v in disallowed_option_ids if v],
        disallowed_option_texts=[str(v) for v in disallowed_option_texts if v],
    )
    return StudentExplanationResultResponse(
        explanation_id=row.id,
        status=row.status,
        explanation=validated,
        created_at=row.created_at,
        updated_at=row.updated_at,
        prompt_version=row.prompt_version,
        model_name=row.model_name,
    )
