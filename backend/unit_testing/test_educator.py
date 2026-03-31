import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.deps import get_current_user, get_db
from app.main import app
from app.models import (
    Assessment,
    Base,
    Enrollment,
    Institution,
    Module,
    Notification,
    Question,
    Submission,
    User,
    UserRole,
    Workshop,
)


@pytest.fixture()
def client_and_state():
    db_path = Path("unit_testing") / f"ut_educator_{uuid4().hex}.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///./{db_path.as_posix()}")
    session_local = async_sessionmaker(bind=engine, expire_on_commit=False)
    state = {"user_id": "educator-1"}

    async def setup_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with session_local() as session:
            inst_one = Institution(id="inst-1", name="IIT Delhi", address="Delhi")
            inst_two = Institution(id="inst-2", name="IIT Kanpur", address="Kanpur")
            admin = User(
                id="admin-1",
                name="Platform Admin",
                email="admin@vidyasetu.edu",
                password="hashed",
                role=UserRole.ADMIN,
                institution_id="inst-1",
            )
            educator = User(
                id="educator-1",
                name="Educator One",
                email="educator@vidyasetu.edu",
                password="hashed",
                role=UserRole.EDUCATOR,
                institution_id="inst-1",
            )
            student = User(
                id="student-1",
                name="Student One",
                email="student1@vidyasetu.edu",
                password="hashed",
                role=UserRole.STUDENT,
                institution_id="inst-1",
            )
            own_workshop = Workshop(
                id="workshop-own",
                title="Educator Workshop",
                description="Owned by educator institution",
                institution_id="inst-1",
                start_date=datetime.now(timezone.utc) - timedelta(days=20),
                end_date=datetime.now(timezone.utc) + timedelta(days=10),
            )
            other_workshop = Workshop(
                id="workshop-other",
                title="External Workshop",
                description="Different institution",
                institution_id="inst-2",
                start_date=datetime.now(timezone.utc) - timedelta(days=20),
                end_date=datetime.now(timezone.utc) + timedelta(days=10),
            )
            module = Module(
                id="module-1",
                workshop_id="workshop-own",
                title="Module One",
                order_index=1,
                materials=[{"id": "mat-1", "title": "Slide deck", "type": "link", "content": "https://example.com"}],
            )
            assessment = Assessment(
                id="assessment-1",
                workshop_id="workshop-own",
                module_id="module-1",
                title="Assessment One",
                total_marks=100,
                pass_mark=40,
            )
            question = Question(
                id="question-1",
                assessment_id="assessment-1",
                text="What is TypeScript?",
                type="mcq",
                marks=10,
                options=[
                    {"id": "opt-a", "text": "Typed JS", "is_correct": True},
                    {"id": "opt-b", "text": "Database", "is_correct": False},
                ],
            )
            enrollment = Enrollment(
                id="enrollment-1",
                student_id="student-1",
                workshop_id="workshop-own",
                status="active",
            )
            submission = Submission(
                id="submission-1",
                student_id="student-1",
                assessment_id="assessment-1",
                score=None,
                percentage=None,
                pass_fail=None,
                answers=[],
            )
            graded_submission = Submission(
                id="submission-graded",
                student_id="student-1",
                assessment_id="assessment-1",
                score=10,
                percentage=100,
                pass_fail=True,
                answers=[{"question_id": "question-1", "selected_option_ids": ["opt-a"]}],
            )
            notification = Notification(
                id="notification-1",
                user_id="educator-1",
                message="New submission pending",
            )

            session.add_all(
                [
                    inst_one,
                    inst_two,
                    admin,
                    educator,
                    student,
                    own_workshop,
                    other_workshop,
                    module,
                    assessment,
                    question,
                    enrollment,
                    submission,
                    graded_submission,
                    notification,
                ]
            )
            await session.commit()

    async def override_get_db():
        async with session_local() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def override_get_current_user():
        async with session_local() as session:
            user = await session.get(User, state["user_id"])
            return user

    asyncio.run(setup_db())
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        yield client, state

    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())
    if db_path.exists():
        db_path.unlink()


def test_educator_dashboard_stats(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/dashboard/educator")
    assert response.status_code == 200
    payload = response.json()
    assert payload["assigned_workshops"] >= 1
    assert payload["active_assessments"] >= 1


def test_educator_workshop_list_is_scoped(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/workshops/")
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["items"]}
    assert "workshop-own" in ids
    assert "workshop-other" not in ids


def test_educator_can_view_assessments_and_submissions(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    assessments_response = client.get("/api/v1/assessments/workshop/workshop-own")
    assert assessments_response.status_code == 200
    assert assessments_response.json()["total"] >= 1

    submissions_response = client.get("/api/v1/submissions/assessment/assessment-1")
    assert submissions_response.status_code == 200
    assert submissions_response.json()["total"] >= 1


def test_educator_can_fetch_workshop_analytics(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/analytics/workshop/workshop-own")
    assert response.status_code == 200
    payload = response.json()
    assert payload["workshop_id"] == "workshop-own"
    assert "assessment" in payload
    assert "pass_rate_percentage" in payload["assessment"]


def test_educator_notifications_success(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/notifications/educator-1")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_educator_can_view_review_and_dispatch_parent_message(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    review = client.get("/api/v1/submissions/submission-graded/review")
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload["submission_id"] == "submission-graded"
    assert len(review_payload["questions"]) >= 1

    message = client.post(
        "/api/v1/communication/parent-email",
        json={
            "student_ids": ["student-1"],
            "subject": "Submission Reviewed",
            "body": "Please check updated breakdown.",
        },
    )
    assert message.status_code == 200
    assert message.json()["accepted"] == 1

    assessment_lb = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1")
    assert assessment_lb.status_code == 200


def test_educator_forbidden_admin_and_delete_routes(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    admin_dashboard = client.get("/api/v1/dashboard/admin")
    assert admin_dashboard.status_code == 403

    delete_workshop = client.delete("/api/v1/workshops/workshop-own")
    assert delete_workshop.status_code == 403
