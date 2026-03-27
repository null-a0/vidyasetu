from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_current_user, get_db, require_role
from app.crud.crud_assessment import (
    append_answers,
    get_submission,
    get_submissions_by_assessment,
    get_submissions_by_student,
)
from app.models import User, UserRole
from app.schemas.assessment import AnswerBatch, SubmissionResponse
from app.schemas.base import Page

router = APIRouter(prefix="/submissions", tags=["submissions"])

_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


# ────────────────────────────────────────────────────────────────────────────
# POST /submissions/{submission_id}/answers  — append/upsert answers
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/{submission_id}/answers",
    response_model=SubmissionResponse,
    summary="Append or replace answers in a submission (student: own only)",
)
async def post_answers(
    submission_id: str,
    payload: AnswerBatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResponse:
    submission = await get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

    # Students can only update their own submission
    if current_user.role == UserRole.STUDENT and submission.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    # Cannot modify a graded submission
    if submission.pass_fail is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot modify answers on an already-graded submission.",
        )

    updated = await append_answers(db, submission, payload)
    return SubmissionResponse.model_validate(updated)


# ────────────────────────────────────────────────────────────────────────────
# GET /submissions/{submission_id}/result  — view score/pass/fail
# ────────────────────────────────────────────────────────────────────────────


@router.get(
    "/{submission_id}/result",
    response_model=SubmissionResponse,
    summary="Get graded result of a submission",
)
async def get_result(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResponse:
    submission = await get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

    # Students see only their own results
    if current_user.role == UserRole.STUDENT and submission.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if submission.pass_fail is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This submission has not been graded yet. Submit first.",
        )

    return SubmissionResponse.model_validate(submission)


# ────────────────────────────────────────────────────────────────────────────
# GET /submissions/student/{student_id}
# ────────────────────────────────────────────────────────────────────────────


@router.get(
    "/student/{student_id}",
    response_model=Page[SubmissionResponse],
    summary="List all submissions for a student",
)
async def list_by_student(
    student_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[SubmissionResponse]:
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    items, total = await get_submissions_by_student(db, student_id, offset=page.offset, limit=page.limit)
    return Page(
        items=[SubmissionResponse.model_validate(s) for s in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


# ────────────────────────────────────────────────────────────────────────────
# GET /submissions/assessment/{assessment_id}  (staff)
# ────────────────────────────────────────────────────────────────────────────


@router.get(
    "/assessment/{assessment_id}",
    response_model=Page[SubmissionResponse],
    summary="List all submissions for an assessment (staff only)",
)
async def list_by_assessment(
    assessment_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> Page[SubmissionResponse]:
    items, total = await get_submissions_by_assessment(db, assessment_id, offset=page.offset, limit=page.limit)
    return Page(
        items=[SubmissionResponse.model_validate(s) for s in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )
