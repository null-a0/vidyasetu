from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.crud.crud_assessment import (
    apply_grade,
    get_assessment,
    get_questions_by_assessment,
    get_submission,
    get_submissions_by_student,
    start_submission,
)
from app.models import User, UserRole
from app.schemas.assessment import (
    GradeResult,
    QuestionPublicResponse,
    SubmissionResponse,
    TestStartResponse,
)
from app.services.grading import grade_submission

router = APIRouter(prefix="/tests", tags=["tests"])


# ────────────────────────────────────────────────────────────────────────────
# POST /tests/{assessment_id}/start
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/{assessment_id}/start",
    response_model=TestStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a test — creates a blank submission and returns questions (no correct answers)",
)
async def start_test(
    assessment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TestStartResponse:
    assessment = await get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")

    # Prevent double-starting: if student already has an un-graded submission, reuse it
    if current_user.role == UserRole.STUDENT:
        existing_items, _ = await get_submissions_by_student(db, current_user.id, limit=200)
        for sub in existing_items:
            if sub.assessment_id == assessment_id and sub.pass_fail is None:
                # Return the existing in-progress submission
                questions, _ = await get_questions_by_assessment(db, assessment_id, limit=200)
                return TestStartResponse(
                    submission_id=sub.id,
                    assessment_id=assessment_id,
                    title=assessment.title or "",
                    total_marks=assessment.total_marks or 0,
                    questions=[QuestionPublicResponse.model_validate(q) for q in questions],
                )

    submission = await start_submission(db, student_id=current_user.id, assessment_id=assessment_id)
    questions, _ = await get_questions_by_assessment(db, assessment_id, limit=200)
    return TestStartResponse(
        submission_id=submission.id,
        assessment_id=assessment_id,
        title=assessment.title or "",
        total_marks=assessment.total_marks or 0,
        questions=[QuestionPublicResponse.model_validate(q) for q in questions],
    )


# ────────────────────────────────────────────────────────────────────────────
# POST /tests/{assessment_id}/submit
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/{assessment_id}/submit",
    response_model=GradeResult,
    summary="Submit test answers — auto-grades MCQ/MSQ, persists score and pass/fail",
)
async def submit_test(
    assessment_id: str,
    submission_id: str,  # passed as query param
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GradeResult:
    assessment = await get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")

    submission = await get_submission(db, submission_id)
    if not submission or submission.assessment_id != assessment_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

    # Students can only submit their own submission
    if current_user.role == UserRole.STUDENT and submission.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    # Already graded?
    if submission.pass_fail is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This submission has already been graded.",
        )

    # Load all questions (up to 500) for grading
    questions, _ = await get_questions_by_assessment(db, assessment_id, limit=500)

    # Run auto-grader
    report = grade_submission(
        questions=list(questions),
        answers=submission.answers or [],
        pass_mark=assessment.pass_mark or 0,
    )

    # Persist grades
    await apply_grade(
        db,
        submission,
        score=report.score,
        total_marks=report.total_marks,
        pass_fail=report.pass_fail,
    )

    return GradeResult(
        submission_id=submission.id,
        score=report.score,
        total_marks=report.total_marks,
        percentage=report.percentage,
        pass_fail=report.pass_fail,
        per_question=[
            {"question_id": d.question_id, "earned": d.earned, "max": d.max_marks}
            for d in report.details
        ],
    )
