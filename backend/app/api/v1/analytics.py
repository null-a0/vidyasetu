from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_role
from app.crud.crud_analytics import (
    get_student_analytics,
    get_student_attendance,
    get_workshop_analytics,
)
from app.crud.crud_workshop import get_workshop
from app.models import (
    Assessment,
    Attendance,
    Enrollment,
    Institution,
    Question,
    Session,
    Submission,
    User,
    UserRole,
    Workshop,
)
from app.schemas.analytics import (
    AdminDashboardInsightsResponse,
    AssessmentLeaderboardResponse,
    DashboardActivityItem,
    DashboardAlertItem,
    DashboardSeriesPoint,
    InstitutionDashboardAggregateResponse,
    InstitutionAttendanceReportResponse,
    InstitutionAttendanceRow,
    InstitutionStudentRosterItem,
    InstitutionStudentRosterResponse,
    LeaderboardEntry,
    LeaderboardAttemptDetail,
    LeaderboardAttemptQuestion,
    LeaderboardStudentDrilldownResponse,
    StudentAnalyticsResponse,
    StudentAttendanceResponse,
    WorkshopLeaderboardResponse,
    WorkshopAnalyticsResponse,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


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
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    result = await get_student_analytics(db, student_id)
    return StudentAnalyticsResponse.model_validate(result)


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
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    result = await get_student_attendance(db, student_id)
    return StudentAttendanceResponse.model_validate(result)


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


@router.get(
    "/leaderboard/assessment/{assessment_id}",
    response_model=AssessmentLeaderboardResponse,
    summary="Assessment leaderboard ranked by average percentage",
)
async def assessment_leaderboard(
    assessment_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> AssessmentLeaderboardResponse:
    assessment = await db.get(Assessment, assessment_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")

    rows = (
        await db.execute(
            select(
                Submission.student_id,
                func.coalesce(User.name, User.email).label("student_name"),
                func.coalesce(func.avg(Submission.percentage), 0).label("avg_percentage"),
                func.count(Submission.id).label("attempts"),
                func.sum(case((Submission.pass_fail == True, 1), else_=0)).label("passed"),  # noqa: E712
            )
            .join(User, User.id == Submission.student_id)
            .where(Submission.assessment_id == assessment_id)
            .group_by(Submission.student_id, User.name, User.email)
            .order_by(func.coalesce(func.avg(Submission.percentage), 0).desc(), func.count(Submission.id).desc())
            .limit(50)
        )
    ).all()

    entries = [
        LeaderboardEntry(
            rank=index + 1,
            student_id=row.student_id,
            student_name=row.student_name,
            average_percentage=round(float(row.avg_percentage or 0), 2),
            attempts=int(row.attempts or 0),
            passed=int(row.passed or 0),
        )
        for index, row in enumerate(rows)
    ]
    return AssessmentLeaderboardResponse(assessment_id=assessment_id, entries=entries)


@router.get(
    "/leaderboard/workshop/{workshop_id}",
    response_model=WorkshopLeaderboardResponse,
    summary="Workshop leaderboard ranked by average percentage across workshop assessments",
)
async def workshop_leaderboard(
    workshop_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> WorkshopLeaderboardResponse:
    workshop = await get_workshop(db, workshop_id)
    if not workshop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workshop not found.")

    assessment_ids = [
        row[0]
        for row in (
            await db.execute(select(Assessment.id).where(Assessment.workshop_id == workshop_id))
        ).all()
    ]
    if not assessment_ids:
        return WorkshopLeaderboardResponse(workshop_id=workshop_id, entries=[])

    rows = (
        await db.execute(
            select(
                Submission.student_id,
                func.coalesce(User.name, User.email).label("student_name"),
                func.coalesce(func.avg(Submission.percentage), 0).label("avg_percentage"),
                func.count(Submission.id).label("attempts"),
                func.sum(case((Submission.pass_fail == True, 1), else_=0)).label("passed"),  # noqa: E712
            )
            .join(User, User.id == Submission.student_id)
            .where(Submission.assessment_id.in_(assessment_ids))
            .group_by(Submission.student_id, User.name, User.email)
            .order_by(func.coalesce(func.avg(Submission.percentage), 0).desc(), func.count(Submission.id).desc())
            .limit(50)
        )
    ).all()

    entries = [
        LeaderboardEntry(
            rank=index + 1,
            student_id=row.student_id,
            student_name=row.student_name,
            average_percentage=round(float(row.avg_percentage or 0), 2),
            attempts=int(row.attempts or 0),
            passed=int(row.passed or 0),
        )
        for index, row in enumerate(rows)
    ]
    return WorkshopLeaderboardResponse(workshop_id=workshop_id, entries=entries)


async def _build_student_leaderboard_drilldown(
    db: AsyncSession,
    *,
    student_id: str,
    context_type: str,
    context_id: str,
    assessment_ids: list[str],
) -> LeaderboardStudentDrilldownResponse:
    student_name = (
        await db.execute(select(func.coalesce(User.name, User.email)).where(User.id == student_id))
    ).scalar_one_or_none()
    if not student_name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    submissions = (
        await db.execute(
            select(Submission)
            .where(Submission.student_id == student_id)
            .where(Submission.assessment_id.in_(assessment_ids))
            .where(Submission.pass_fail.is_not(None))
            .order_by(Submission.submitted_at.desc())
            .limit(10)
        )
    ).scalars().all()

    attempt_details: list[LeaderboardAttemptDetail] = []
    percentages: list[float] = []
    for submission in submissions:
        questions = (
            await db.execute(select(Question).where(Question.assessment_id == submission.assessment_id))
        ).scalars().all()
        answers_lookup = {
            item.get("question_id"): item.get("selected_option_ids", [])
            for item in (submission.answers or [])
            if isinstance(item, dict)
        }

        question_rows: list[LeaderboardAttemptQuestion] = []
        for question in questions:
            options = question.options or []
            correct_ids = [opt.get("id") for opt in options if opt.get("is_correct")]
            selected_ids = answers_lookup.get(question.id, [])
            selected_texts = [opt.get("text", "") for opt in options if opt.get("id") in selected_ids]
            correct_texts = [opt.get("text", "") for opt in options if opt.get("id") in correct_ids]
            max_marks = int(question.marks or 0)
            is_correct = sorted(selected_ids) == sorted(correct_ids)
            question_rows.append(
                LeaderboardAttemptQuestion(
                    question_id=question.id,
                    question_text=question.text or "",
                    selected_option_texts=selected_texts,
                    correct_option_texts=correct_texts,
                    earned_marks=max_marks if is_correct else 0,
                    max_marks=max_marks,
                    is_correct=is_correct,
                )
            )

        percentage = float(submission.percentage or 0)
        percentages.append(percentage)
        attempt_details.append(
            LeaderboardAttemptDetail(
                submission_id=submission.id,
                submitted_at=submission.submitted_at.isoformat() if submission.submitted_at else None,
                score=float(submission.score or 0),
                percentage=percentage,
                pass_fail=bool(submission.pass_fail),
                questions=question_rows,
            )
        )

    average = round(sum(percentages) / len(percentages), 2) if percentages else 0.0
    return LeaderboardStudentDrilldownResponse(
        context_type=context_type,
        context_id=context_id,
        student_id=student_id,
        student_name=student_name,
        attempts=attempt_details,
        average_percentage=average,
        total_attempts=len(attempt_details),
    )


@router.get(
    "/leaderboard/assessment/{assessment_id}/student/{student_id}",
    response_model=LeaderboardStudentDrilldownResponse,
    summary="Detailed leaderboard drilldown for one student in an assessment",
)
async def assessment_leaderboard_drilldown(
    assessment_id: str,
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> LeaderboardStudentDrilldownResponse:
    assessment = await db.get(Assessment, assessment_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    return await _build_student_leaderboard_drilldown(
        db,
        student_id=student_id,
        context_type="assessment",
        context_id=assessment_id,
        assessment_ids=[assessment_id],
    )


@router.get(
    "/leaderboard/workshop/{workshop_id}/student/{student_id}",
    response_model=LeaderboardStudentDrilldownResponse,
    summary="Detailed leaderboard drilldown for one student across a workshop",
)
async def workshop_leaderboard_drilldown(
    workshop_id: str,
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> LeaderboardStudentDrilldownResponse:
    workshop = await get_workshop(db, workshop_id)
    if not workshop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workshop not found.")
    assessment_ids = [
        row[0]
        for row in (await db.execute(select(Assessment.id).where(Assessment.workshop_id == workshop_id))).all()
    ]
    return await _build_student_leaderboard_drilldown(
        db,
        student_id=student_id,
        context_type="workshop",
        context_id=workshop_id,
        assessment_ids=assessment_ids,
    )


@router.get(
    "/institution/dashboard",
    response_model=InstitutionDashboardAggregateResponse,
    summary="Institution dashboard aggregate/reporting data",
)
async def institution_dashboard_aggregate(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> InstitutionDashboardAggregateResponse:
    institution_id = current_user.institution_id if current_user.role == UserRole.INSTITUTION_ADMIN else None

    workshop_query = select(Workshop.id)
    if institution_id:
        workshop_query = workshop_query.where(Workshop.institution_id == institution_id)
    workshop_ids = [row[0] for row in (await db.execute(workshop_query)).all()]

    if not workshop_ids:
        return InstitutionDashboardAggregateResponse(
            kpis={"workshops": 0, "educators": 0, "students": 0, "active_assessments": 0},
            alerts=[],
            activity_feed=[],
            attendance_trend=[],
            enrollment_trend=[],
            report_cards={"average_score": 0, "completion_rate": 0, "pass_rate": 0, "top_workshop": "—"},
        )

    educators_query = select(func.count(User.id)).where(User.role == UserRole.EDUCATOR)
    students_query = select(func.count(User.id)).where(User.role == UserRole.STUDENT)
    if institution_id:
        educators_query = educators_query.where(User.institution_id == institution_id)
        students_query = students_query.where(User.institution_id == institution_id)

    assessment_count_query = select(func.count(Assessment.id)).where(Assessment.workshop_id.in_(workshop_ids))
    total_enrollments_query = select(func.count(Enrollment.id)).where(Enrollment.workshop_id.in_(workshop_ids))
    completed_enrollments_query = (
        select(func.count(Enrollment.id))
        .where(Enrollment.workshop_id.in_(workshop_ids))
        .where(Enrollment.status == "completed")
    )
    pending_submissions_query = (
        select(func.count(Submission.id))
        .join(Assessment, Assessment.id == Submission.assessment_id)
        .where(Assessment.workshop_id.in_(workshop_ids))
        .where(Submission.pass_fail.is_(None))
    )
    submission_metrics_query = (
        select(
            func.coalesce(func.avg(Submission.percentage), 0),
            func.sum(case((Submission.pass_fail == True, 1), else_=0)),  # noqa: E712
            func.count(Submission.id),
        )
        .join(Assessment, Assessment.id == Submission.assessment_id)
        .where(Assessment.workshop_id.in_(workshop_ids))
    )

    educators = int((await db.execute(educators_query)).scalar_one() or 0)
    students = int((await db.execute(students_query)).scalar_one() or 0)
    assessment_count = int((await db.execute(assessment_count_query)).scalar_one() or 0)
    total_enrollments = int((await db.execute(total_enrollments_query)).scalar_one() or 0)
    completed_enrollments = int((await db.execute(completed_enrollments_query)).scalar_one() or 0)
    pending_submissions = int((await db.execute(pending_submissions_query)).scalar_one() or 0)
    avg_score, passed_count, total_submissions = (await db.execute(submission_metrics_query)).one()
    pass_rate = round((float(passed_count or 0) / float(total_submissions or 1)) * 100, 2) if total_submissions else 0.0
    completion_rate = round((completed_enrollments / total_enrollments) * 100, 2) if total_enrollments else 0.0

    top_workshop = (
        await db.execute(
            select(Workshop.title, func.count(Enrollment.id).label("enrolled"))
            .outerjoin(Enrollment, Enrollment.workshop_id == Workshop.id)
            .where(Workshop.id.in_(workshop_ids))
            .group_by(Workshop.id, Workshop.title)
            .order_by(func.count(Enrollment.id).desc())
            .limit(1)
        )
    ).first()

    now = datetime.now(timezone.utc)
    recent_submissions = (
        await db.execute(
            select(Submission.submitted_at, Assessment.title)
            .join(Assessment, Assessment.id == Submission.assessment_id)
            .where(Assessment.workshop_id.in_(workshop_ids))
            .order_by(Submission.submitted_at.desc())
            .limit(3)
        )
    ).all()
    recent_enrollments = (
        await db.execute(
            select(Enrollment.enrolled_at, Workshop.title)
            .join(Workshop, Workshop.id == Enrollment.workshop_id)
            .where(Enrollment.workshop_id.in_(workshop_ids))
            .order_by(Enrollment.enrolled_at.desc())
            .limit(3)
        )
    ).all()

    activity_feed: list[DashboardActivityItem] = []
    for index, row in enumerate(recent_submissions):
        activity_feed.append(
            DashboardActivityItem(
                id=f"submission-{index}",
                text=f"Submission received for {row.title or 'assessment'}",
                time=(row.submitted_at or now).isoformat(),
                type="submission",
            )
        )
    for index, row in enumerate(recent_enrollments):
        activity_feed.append(
            DashboardActivityItem(
                id=f"enrollment-{index}",
                text=f"Enrollment added to {row.title or 'workshop'}",
                time=(row.enrolled_at or now).isoformat(),
                type="enrollment",
            )
        )
    if not activity_feed:
        activity_feed = [DashboardActivityItem(id="activity-0", text="No recent activity yet.", time=now.isoformat(), type="system")]
    activity_feed.sort(key=lambda item: item.time, reverse=True)
    activity_feed = activity_feed[:6]

    attendance_rows = (
        await db.execute(
            select(Session.start_time, Attendance.status)
            .join(Attendance, Attendance.session_id == Session.id)
            .where(Session.workshop_id.in_(workshop_ids))
            .where(Session.start_time.is_not(None))
            .where(Session.start_time >= now - timedelta(days=6))
            .order_by(Session.start_time.asc())
        )
    ).all()
    attendance_map: dict[str, dict[str, int]] = {}
    for row in attendance_rows:
        date_key = (row.start_time or now).date().isoformat()
        bucket = attendance_map.setdefault(date_key, {"present_like": 0, "total": 0})
        status_text = (row.status or "").lower()
        if status_text in {"present", "late"}:
            bucket["present_like"] += 1
        bucket["total"] += 1
    attendance_trend: list[DashboardSeriesPoint] = []
    for offset in range(6, -1, -1):
        day = (now - timedelta(days=offset)).date()
        date_key = day.isoformat()
        bucket = attendance_map.get(date_key, {"present_like": 0, "total": 0})
        ratio = round((bucket["present_like"] / bucket["total"]) * 100, 2) if bucket["total"] else 0.0
        attendance_trend.append(DashboardSeriesPoint(label=day.strftime("%a"), value=ratio))

    enrollment_rows = (
        await db.execute(
            select(Enrollment.enrolled_at)
            .where(Enrollment.workshop_id.in_(workshop_ids))
            .where(Enrollment.enrolled_at.is_not(None))
            .where(Enrollment.enrolled_at >= now - timedelta(weeks=5))
            .order_by(Enrollment.enrolled_at.asc())
        )
    ).all()
    enrollment_count_by_week: dict[str, int] = {}
    for row in enrollment_rows:
        enrolled_at = row.enrolled_at or now
        start_of_week = enrolled_at.date() - timedelta(days=enrolled_at.date().weekday())
        key = start_of_week.isoformat()
        enrollment_count_by_week[key] = enrollment_count_by_week.get(key, 0) + 1
    enrollment_trend: list[DashboardSeriesPoint] = []
    for offset in range(5, -1, -1):
        week_anchor = (now - timedelta(weeks=offset)).date()
        start_of_week = week_anchor - timedelta(days=week_anchor.weekday())
        enrollment_trend.append(
            DashboardSeriesPoint(
                label=start_of_week.strftime("%b %d"),
                value=float(enrollment_count_by_week.get(start_of_week.isoformat(), 0)),
            )
        )

    return InstitutionDashboardAggregateResponse(
        kpis={
            "workshops": len(workshop_ids),
            "educators": educators,
            "students": students,
            "active_assessments": assessment_count,
        },
        alerts=[
            DashboardAlertItem(id="alert-1", text=f"{assessment_count} assessments available.", level="info"),
            DashboardAlertItem(
                id="alert-2",
                text=f"{pending_submissions} submissions pending grading.",
                level="warning" if pending_submissions > 0 else "success",
            ),
        ],
        activity_feed=activity_feed,
        attendance_trend=attendance_trend,
        enrollment_trend=enrollment_trend,
        report_cards={
            "average_score": round(float(avg_score or 0), 2),
            "completion_rate": completion_rate,
            "pass_rate": round(pass_rate, 2),
            "top_workshop": top_workshop[0] if top_workshop else "—",
        },
    )


@router.get(
    "/institution/students",
    response_model=InstitutionStudentRosterResponse,
    summary="Institution-wide student roster for dashboard students tab",
)
async def institution_student_roster(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> InstitutionStudentRosterResponse:
    institution_id = current_user.institution_id if current_user.role == UserRole.INSTITUTION_ADMIN else None
    students_query = select(User).where(User.role == UserRole.STUDENT)
    if institution_id:
        students_query = students_query.where(User.institution_id == institution_id)
    students = (await db.execute(students_query.order_by(User.name.asc()))).scalars().all()
    if not students:
        return InstitutionStudentRosterResponse(items=[], total=0)

    student_ids = [student.id for student in students]
    enrollment_rows = (
        await db.execute(
            select(Enrollment.student_id, Enrollment.status, Workshop.title)
            .join(Workshop, Workshop.id == Enrollment.workshop_id)
            .where(Enrollment.student_id.in_(student_ids))
            .order_by(Enrollment.enrolled_at.desc())
        )
    ).all()
    first_enrollment_by_student: dict[str, tuple[str, str]] = {}
    for row in enrollment_rows:
        if row.student_id not in first_enrollment_by_student:
            status_text = (row.status.value if hasattr(row.status, "value") else str(row.status or "")).lower()
            if status_text == "active":
                ui_status = "Active"
            elif status_text == "completed":
                ui_status = "Completed"
            else:
                ui_status = "Inactive"
            first_enrollment_by_student[row.student_id] = (row.title or "—", ui_status)

    items = []
    for student in students:
        workshop_title, ui_status = first_enrollment_by_student.get(student.id, ("—", "Inactive"))
        items.append(
            InstitutionStudentRosterItem(
                id=student.id,
                name=student.name or student.email,
                email=student.email,
                workshop=workshop_title,
                status=ui_status,
            )
        )
    return InstitutionStudentRosterResponse(items=items, total=len(items))


@router.get(
    "/institution/attendance-report",
    response_model=InstitutionAttendanceReportResponse,
    summary="Institution attendance report rows for dashboard attendance tab",
)
async def institution_attendance_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> InstitutionAttendanceReportResponse:
    institution_id = current_user.institution_id if current_user.role == UserRole.INSTITUTION_ADMIN else None
    workshop_query = select(Workshop.id)
    if institution_id:
        workshop_query = workshop_query.where(Workshop.institution_id == institution_id)
    workshop_ids = [row[0] for row in (await db.execute(workshop_query)).all()]
    if not workshop_ids:
        return InstitutionAttendanceReportResponse(rows=[], total=0)

    now = datetime.now(timezone.utc)
    week_start = now.date() - timedelta(days=now.date().weekday())
    week_end = week_start + timedelta(days=4)

    attendance_rows = (
        await db.execute(
            select(User.name, Session.start_time, Attendance.status)
            .join(Attendance, Attendance.student_id == User.id)
            .join(Session, Session.id == Attendance.session_id)
            .where(User.role == UserRole.STUDENT)
            .where(Session.workshop_id.in_(workshop_ids))
            .where(Session.start_time.is_not(None))
            .where(Session.start_time >= datetime.combine(week_start, datetime.min.time(), tzinfo=timezone.utc))
            .where(Session.start_time <= datetime.combine(week_end, datetime.max.time(), tzinfo=timezone.utc))
            .order_by(User.name.asc(), Session.start_time.asc())
        )
    ).all()

    status_by_student_day: dict[str, dict[int, bool]] = {}
    for row in attendance_rows:
        student_name = row.name or "Student"
        weekday = (row.start_time or now).weekday()
        if weekday > 4:
            continue
        status_text = (row.status or "").lower()
        present = status_text in {"present", "late"}
        status_by_student_day.setdefault(student_name, {})[weekday] = present

    rows: list[InstitutionAttendanceRow] = []
    for student_name, day_map in status_by_student_day.items():
        rows.append(
            InstitutionAttendanceRow(
                student=student_name,
                mon=bool(day_map.get(0, False)),
                tue=bool(day_map.get(1, False)),
                wed=bool(day_map.get(2, False)),
                thu=bool(day_map.get(3, False)),
                fri=bool(day_map.get(4, False)),
            )
        )
    return InstitutionAttendanceReportResponse(rows=rows, total=len(rows))


@router.get(
    "/admin/insights",
    response_model=AdminDashboardInsightsResponse,
    summary="Admin dashboard insights for charts/activity feed",
)
async def admin_insights(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
) -> AdminDashboardInsightsResponse:
    now = datetime.now(timezone.utc)
    submission_rows = (
        await db.execute(
            select(Submission.submitted_at)
            .where(Submission.submitted_at.is_not(None))
            .where(Submission.submitted_at >= now - timedelta(days=6))
            .order_by(Submission.submitted_at.asc())
        )
    ).all()
    submissions_by_day: dict[str, int] = {}
    for row in submission_rows:
        date_key = (row.submitted_at or now).date().isoformat()
        submissions_by_day[date_key] = submissions_by_day.get(date_key, 0) + 1
    weekly_activity = [
        DashboardSeriesPoint(
            label=(now - timedelta(days=offset)).strftime("%a"),
            value=float(submissions_by_day.get((now - timedelta(days=offset)).date().isoformat(), 0)),
        )
        for offset in range(6, -1, -1)
    ]

    institution_student_counts = (
        await db.execute(
            select(Institution.name, func.count(User.id))
            .select_from(Institution)
            .outerjoin(User, (User.institution_id == Institution.id) & (User.role == UserRole.STUDENT))
            .group_by(Institution.id, Institution.name)
            .order_by(func.count(User.id).desc())
            .limit(5)
        )
    ).all()
    demographics = [
        {"range": row[0] or "Unknown", "male": int(row[1] or 0), "female": 0}
        for row in institution_student_counts
    ]

    recent_submissions = (
        await db.execute(
            select(Submission.submitted_at, Assessment.title)
            .join(Assessment, Assessment.id == Submission.assessment_id)
            .order_by(Submission.submitted_at.desc())
            .limit(3)
        )
    ).all()
    recent_enrollments = (
        await db.execute(
            select(Enrollment.enrolled_at, Workshop.title)
            .join(Workshop, Workshop.id == Enrollment.workshop_id)
            .order_by(Enrollment.enrolled_at.desc())
            .limit(3)
        )
    ).all()
    activity_feed: list[DashboardActivityItem] = []
    for index, row in enumerate(recent_submissions):
        activity_feed.append(
            DashboardActivityItem(
                id=f"admin-sub-{index}",
                text=f"Submission received for {row.title or 'assessment'}",
                time=(row.submitted_at or now).isoformat(),
                type="submission",
            )
        )
    for index, row in enumerate(recent_enrollments):
        activity_feed.append(
            DashboardActivityItem(
                id=f"admin-enr-{index}",
                text=f"Enrollment created for {row.title or 'workshop'}",
                time=(row.enrolled_at or now).isoformat(),
                type="enrollment",
            )
        )
    if not activity_feed:
        activity_feed = [DashboardActivityItem(id="admin-0", text="No recent activity yet.", time=now.isoformat(), type="system")]
    activity_feed.sort(key=lambda item: item.time, reverse=True)
    activity_feed = activity_feed[:6]

    return AdminDashboardInsightsResponse(
        weekly_activity=weekly_activity,
        demographics=demographics,
        activity_feed=activity_feed,
    )
