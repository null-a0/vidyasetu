from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.config import settings
from app.crud.crud_ai_generation import (
    create_ai_generation,
    fail_stale_active_generations,
    find_active_generation_by_fingerprint,
    find_cached_completed_generation,
    update_ai_generation,
)
from app.crud.crud_assessment import get_question, get_submission
from app.models import AIFeatureType, AIGenerationStatus, User, UserRole
from app.schemas.ai import (
    STUDENT_EXPLANATION_RESPONSE_JSON_SCHEMA,
    AIGenerationCreate,
    AIGenerationUpdate,
    AITokenUsage,
    StudentExplanationCreateRequest,
    StudentExplanationCreateResponse,
)
from app.services.ai.cache import (
    build_student_explanation_request_fingerprint,
    compute_cache_expiry,
)
from app.services.ai.gemini_client import GeminiClient
from app.services.ai.rate_limit import (
    DatabaseFixedWindowRateLimiter,
    InMemorySlidingWindowRateLimiter,
    RateLimitRule,
    RateLimitViolation,
    consume_rate_limit_or_raise,
)
from app.services.ai.student_explanation_prompt import build_student_explanation_prompt
from app.services.ai.validation import validate_student_explanation_output

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


def get_gemini_client() -> GeminiClient:
    return GeminiClient.from_settings()


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
    gemini_client: GeminiClient = Depends(get_gemini_client),
    limiter: InMemorySlidingWindowRateLimiter | DatabaseFixedWindowRateLimiter = Depends(
        get_student_explanation_rate_limiter
    ),
    rate_rule: RateLimitRule = Depends(get_student_explanation_rate_limit_rule),
) -> StudentExplanationCreateResponse:
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

    prompt_payload = {
        "question_id": question.id,
        "question_text": question.text or "",
        "question_type": question.type.value if hasattr(question.type, "value") else str(question.type or ""),
        "student_selected_option_texts": selected_option_texts,
        "student_selected_option_ids": selected_option_ids,
        "correct_option_texts_internal_only": correct_option_texts,
    }
    request_fingerprint = build_student_explanation_request_fingerprint(
        student_id=current_user.id,
        submission_id=submission.id,
        question_id=question.id,
        prompt_version=settings.AI_STUDENT_EXPLANATION_PROMPT_VERSION,
        model_name=settings.GEMINI_MODEL_NAME,
        raw_prompt_input=prompt_payload,
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
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Explanation generation is already in progress. Please retry shortly.",
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
            raw_prompt_input=prompt_payload,
            request_fingerprint=request_fingerprint,
            cache_expires_at=compute_cache_expiry(
                ttl_seconds=settings.AI_STUDENT_EXPLANATION_CACHE_TTL_SECONDS
            ),
        ),
    )
    await update_ai_generation(
        db,
        generation,
        AIGenerationUpdate(status=AIGenerationStatus.PROCESSING),
    )

    prompt = build_student_explanation_prompt(prompt_payload=prompt_payload)
    try:
        result = await gemini_client.generate_structured(
            prompt=prompt,
            response_json_schema=STUDENT_EXPLANATION_RESPONSE_JSON_SCHEMA,
        )
        validated = validate_student_explanation_output(
            result.parsed_output,
            disallowed_option_ids=correct_option_ids,
            disallowed_option_texts=correct_option_texts,
        )
        generation = await update_ai_generation(
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
                cache_expires_at=compute_cache_expiry(
                    ttl_seconds=settings.AI_STUDENT_EXPLANATION_CACHE_TTL_SECONDS
                ),
            ),
        )
    except Exception as exc:
        await update_ai_generation(
            db,
            generation,
            AIGenerationUpdate(
                status=AIGenerationStatus.FAILED,
                error_details={
                    "error_type": exc.__class__.__name__,
                    "message": str(exc),
                },
            ),
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": "Explanation generation failed.",
                "explanation_id": generation.id,
            },
        )

    return StudentExplanationCreateResponse(
        explanation_id=generation.id,
        status=generation.status,
        from_cache=False,
        explanation=validated,
    )
