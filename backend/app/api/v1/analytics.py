from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_role
from app.crud.crud_analytics import (
    get_student_analytics,
    get_student_attendance,
    get_workshop_analytics,
)
from app.crud.crud_workshop import get_workshop
from app.models import User, UserRole
from app.schemas.analytics import (
    StudentAnalyticsResponse,
    StudentAttendanceResponse,
    WorkshopAnalyticsResponse,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


# ────────────────────────────────────────────────────────────────────────────
# GET /analytics/student/{student_id}
# ────────────────────────────────────────────────────────────────────────────


@router.get(
    "/student/{student_id}",
    response_model=StudentAnalyticsResponse,
    summary="Get performance trends, average scores, and attendance % for a student",
)
async def student_analytics(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentAnalyticsResponse:
    # Students can only see their own analytics
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    result = await get_student_analytics(db, student_id)
    return StudentAnalyticsResponse.model_validate(result)


# ────────────────────────────────────────────────────────────────────────────
# GET /analytics/attendance/{student_id}
# ────────────────────────────────────────────────────────────────────────────


@router.get(
    "/attendance/{student_id}",
    response_model=StudentAttendanceResponse,
    summary="Get detailed chronological attendance records for a student",
)
async def student_attendance(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentAttendanceResponse:
    # Students can only see their own attendance
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    result = await get_student_attendance(db, student_id)
    return StudentAttendanceResponse.model_validate(result)


# ────────────────────────────────────────────────────────────────────────────
# GET /analytics/workshop/{workshop_id}
# ────────────────────────────────────────────────────────────────────────────


@router.get(
    "/workshop/{workshop_id}",
    response_model=WorkshopAnalyticsResponse,
    summary="Get cohort-level averages and pass rates for a workshop (staff only)",
)
async def workshop_analytics(
    workshop_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> WorkshopAnalyticsResponse:
    workshop = await get_workshop(db, workshop_id)
    if not workshop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workshop not found.")

    result = await get_workshop_analytics(db, workshop_id)
    return WorkshopAnalyticsResponse.model_validate(result)
