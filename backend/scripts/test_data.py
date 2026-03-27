"""
scripts/test_data.py
--------------------
Resets the local database and loads linked demo data across all core tables.

Run: python -m scripts.test_data
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from app.core.security import hash_password
from app.db import AsyncSessionLocal, engine
from app.models import (
    Assessment,
    Attendance,
    Base,
    Certificate,
    Enrollment,
    EnrollmentStatus,
    FeePlan,
    Institution,
    Module,
    Notification,
    NotificationStatus,
    NotificationType,
    Payment,
    Question,
    QuestionType,
    Session,
    StudentFee,
    Submission,
    User,
    UserRole,
    Workshop,
)
from app.services.certificate import generate_certificate_pdf


PASSWORDS = {
    "admin@vidyasetu.edu": "admin123",
    "institution.admin@vidyasetu.edu": "institution123",
    "educator@vidyasetu.edu": "educator123",
    "student@vidyasetu.edu": "student123",
}
DEFAULT_PASSWORD = "demo123"


def dt(days_from_now: int, hour: int = 10) -> datetime:
    base = datetime.now(tz=UTC).replace(minute=0, second=0, microsecond=0)
    return base + timedelta(days=days_from_now, hours=hour - base.hour)


def materials_for(workshop_title: str, module_index: int) -> list[dict[str, str]]:
    return [
        {
            "id": f"{workshop_title.lower().replace(' ', '-')}-m{module_index}-video",
            "title": f"Lesson {module_index}: Foundations",
            "type": "video",
            "content": f"https://example.com/{workshop_title.lower().replace(' ', '-')}/lesson-{module_index}",
            "created_at": dt(-14 + module_index).isoformat(),
        },
        {
            "id": f"{workshop_title.lower().replace(' ', '-')}-m{module_index}-notes",
            "title": f"Module {module_index} Notes",
            "type": "text",
            "content": f"Detailed notes for {workshop_title}, module {module_index}.",
            "created_at": dt(-14 + module_index).isoformat(),
        },
        {
            "id": f"{workshop_title.lower().replace(' ', '-')}-m{module_index}-resource",
            "title": f"Module {module_index} Resource",
            "type": "link",
            "content": "https://vidyasetu.local/resource",
            "created_at": dt(-13 + module_index).isoformat(),
        },
    ]


async def load_test_data() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        institution_names = [
            "VidyaSetu HQ",
            "North Campus",
            "South Campus",
            "East Campus",
            "West Campus",
            "Central Academy",
            "Horizon Institute",
            "Summit Learning Hub",
            "Riverdale Center",
            "Future Skills School",
        ]
        institutions: list[Institution] = []
        for index, name in enumerate(institution_names, start=1):
            institutions.append(
                Institution(
                    name=name,
                    address=f"{index} Knowledge Park, Chennai",
                )
            )
        db.add_all(institutions)
        await db.flush()

        users: list[User] = []
        admin = User(
            name="VidyaSetu Admin",
            email="admin@vidyasetu.edu",
            password=hash_password(PASSWORDS["admin@vidyasetu.edu"]),
            role=UserRole.ADMIN,
            institution_id=institutions[0].id,
            phone="+91 90000 00001",
            theme="light",
        )
        users.append(admin)

        institution_admins: list[User] = []
        for index, institution in enumerate(institutions, start=1):
            email = "institution.admin@vidyasetu.edu" if index == 1 else f"institution.admin{index}@vidyasetu.edu"
            admin_user = User(
                name=f"{institution.name} Admin",
                email=email,
                password=hash_password(PASSWORDS.get(email, DEFAULT_PASSWORD)),
                role=UserRole.INSTITUTION_ADMIN,
                institution_id=institution.id,
                phone=f"+91 91000 {index:05d}",
                theme="dark" if index % 2 == 0 else "light",
            )
            institution_admins.append(admin_user)
            users.append(admin_user)

        educator_names = [
            "Demo Educator",
            "Asha Menon",
            "Ravi Narayan",
            "Priya Shah",
            "Karthik Iyer",
            "Meera Kulkarni",
        ]
        educators: list[User] = []
        for index, name in enumerate(educator_names, start=1):
            email = "educator@vidyasetu.edu" if index == 1 else f"educator{index}@vidyasetu.edu"
            educators.append(
                User(
                    name=name,
                    email=email,
                    password=hash_password(PASSWORDS.get(email, DEFAULT_PASSWORD)),
                    role=UserRole.EDUCATOR,
                    institution_id=institutions[(index - 1) % 6].id,
                    phone=f"+91 92000 {index:05d}",
                    theme="dark" if index % 2 else "light",
                )
            )
        users.extend(educators)

        student_names = [
            "Demo Student",
            "Arjun Rao",
            "Nisha Patel",
            "Devika Singh",
            "Rahul Nair",
            "Sneha Joshi",
            "Harish Kumar",
            "Ishita Ghosh",
            "Ananya Das",
            "Vikram Sen",
            "Ritika Jain",
            "Kabir Ali",
            "Neha Reddy",
            "Sanjay Pillai",
            "Lavanya Krishnan",
        ]
        students: list[User] = []
        for index, name in enumerate(student_names, start=1):
            email = "student@vidyasetu.edu" if index == 1 else f"student{index}@vidyasetu.edu"
            students.append(
                User(
                    name=name,
                    email=email,
                    password=hash_password(PASSWORDS.get(email, DEFAULT_PASSWORD)),
                    role=UserRole.STUDENT,
                    institution_id=institutions[(index - 1) % 5].id,
                    phone=f"+91 93000 {index:05d}",
                    theme="dark" if index % 3 == 0 else "light",
                )
            )
        users.extend(students)

        db.add_all(users)
        await db.flush()

        for institution, admin_user in zip(institutions, institution_admins):
            institution.admin_id = admin_user.id

        workshop_specs = [
            ("Full Stack Web Bootcamp", 0, -30, 45),
            ("Python for Data Analysis", 0, -21, 30),
            ("UI UX Design Sprint", 1, -15, 20),
            ("Cloud Fundamentals", 1, -10, 40),
            ("Machine Learning Basics", 2, -25, 35),
            ("Data Visualization Studio", 2, -8, 28),
            ("Cybersecurity Essentials", 3, -18, 32),
            ("Communication for Engineers", 3, -5, 18),
            ("Mobile App Prototyping", 4, -14, 24),
            ("DevOps in Practice", 4, -12, 26),
            ("AI Productivity Lab", 5, -7, 21),
            ("Digital Marketing Foundations", 6, -9, 22),
            ("Career Readiness Program", 7, -16, 19),
            ("Financial Literacy Workshop", 8, -11, 17),
            ("Research Writing Intensive", 9, -20, 29),
        ]
        workshops: list[Workshop] = []
        for title, institution_index, start_offset, duration_days in workshop_specs:
            start_date = dt(start_offset, 9)
            workshops.append(
                Workshop(
                    title=title,
                    description=f"{title} with guided modules, assessments, and live sessions.",
                    start_date=start_date,
                    end_date=start_date + timedelta(days=duration_days),
                    institution_id=institutions[institution_index].id,
                )
            )
        db.add_all(workshops)
        await db.flush()

        modules: list[Module] = []
        modules_by_workshop: dict[str, list[Module]] = defaultdict(list)
        for workshop in workshops:
            for module_index in range(1, 3):
                module = Module(
                    workshop_id=workshop.id,
                    title=f"{workshop.title} Module {module_index}",
                    order_index=module_index,
                    materials=materials_for(workshop.title, module_index),
                )
                modules.append(module)
                modules_by_workshop[workshop.id].append(module)
        db.add_all(modules)
        await db.flush()

        students_by_institution: dict[str, list[User]] = defaultdict(list)
        for student in students:
            students_by_institution[student.institution_id].append(student)

        enrollments: list[Enrollment] = []
        for workshop_index, workshop in enumerate(workshops):
            eligible_students = students_by_institution[workshop.institution_id]
            for student_index, student in enumerate(eligible_students[:4]):
                status_cycle = [EnrollmentStatus.ACTIVE, EnrollmentStatus.COMPLETED, EnrollmentStatus.ACTIVE, EnrollmentStatus.DROPPED]
                enrollments.append(
                    Enrollment(
                        student_id=student.id,
                        workshop_id=workshop.id,
                        status=status_cycle[(workshop_index + student_index) % len(status_cycle)],
                        enrolled_at=workshop.start_date - timedelta(days=7 - student_index),
                    )
                )
        db.add_all(enrollments)
        await db.flush()

        enrollments_by_workshop: dict[str, list[Enrollment]] = defaultdict(list)
        for enrollment in enrollments:
            enrollments_by_workshop[enrollment.workshop_id].append(enrollment)

        sessions: list[Session] = []
        for workshop_index, workshop in enumerate(workshops[:10]):
            for session_index in range(1, 3):
                start_time = workshop.start_date + timedelta(days=session_index * 5, hours=1)
                sessions.append(
                    Session(
                        workshop_id=workshop.id,
                        title=f"{workshop.title} Live Session {session_index}",
                        start_time=start_time,
                        end_time=start_time + timedelta(hours=2),
                    )
                )
        db.add_all(sessions)
        await db.flush()

        attendance_rows: list[Attendance] = []
        for session_index, session in enumerate(sessions):
            session_enrollments = enrollments_by_workshop[session.workshop_id][:4]
            for row_index, enrollment in enumerate(session_enrollments):
                attendance_rows.append(
                    Attendance(
                        session_id=session.id,
                        student_id=enrollment.student_id,
                        status=["present", "present", "late", "absent"][(session_index + row_index) % 4],
                    )
                )
        db.add_all(attendance_rows)
        await db.flush()

        assessments: list[Assessment] = []
        assessment_modules: list[Module] = []
        for workshop in workshops:
            module = modules_by_workshop[workshop.id][0]
            assessment = Assessment(
                workshop_id=workshop.id,
                module_id=module.id,
                title=f"{workshop.title} Checkpoint Test",
                total_marks=40,
                pass_mark=18,
            )
            assessments.append(assessment)
            assessment_modules.append(module)
        db.add_all(assessments)
        await db.flush()

        questions: list[Question] = []
        for assessment_index, assessment in enumerate(assessments):
            for question_index in range(1, 5):
                questions.append(
                    Question(
                        assessment_id=assessment.id,
                        text=f"Question {question_index} for {assessment.title}",
                        type=QuestionType.MCQ if question_index % 2 else QuestionType.MSQ,
                        marks=10,
                        options=[
                            {"id": f"q{assessment_index}-{question_index}-a", "text": "Option A", "is_correct": True},
                            {"id": f"q{assessment_index}-{question_index}-b", "text": "Option B", "is_correct": question_index % 2 == 0},
                            {"id": f"q{assessment_index}-{question_index}-c", "text": "Option C", "is_correct": False},
                            {"id": f"q{assessment_index}-{question_index}-d", "text": "Option D", "is_correct": False},
                        ],
                    )
                )
        db.add_all(questions)
        await db.flush()

        questions_by_assessment: dict[str, list[Question]] = defaultdict(list)
        for question in questions:
            questions_by_assessment[question.assessment_id].append(question)

        submissions: list[Submission] = []
        for assessment_index, assessment in enumerate(assessments[:10]):
            workshop_enrollments = [
                enrollment
                for enrollment in enrollments_by_workshop[assessment.workshop_id]
                if enrollment.status != EnrollmentStatus.DROPPED
            ][:3]
            for submission_index, enrollment in enumerate(workshop_enrollments):
                score = 24 + ((assessment_index + submission_index) % 3) * 8
                submissions.append(
                    Submission(
                        student_id=enrollment.student_id,
                        assessment_id=assessment.id,
                        score=score,
                        percentage=int((score / 40) * 100),
                        pass_fail=score >= assessment.pass_mark,
                        answers=[
                            {
                                "question_id": question.id,
                                "selected_option_ids": [question.options[0]["id"]],
                            }
                            for question in questions_by_assessment[assessment.id]
                        ],
                        submitted_at=dt(-5 + submission_index),
                    )
                )
        db.add_all(submissions)
        await db.flush()

        certificates: list[Certificate] = []
        completed_enrollments = [enrollment for enrollment in enrollments if enrollment.status == EnrollmentStatus.COMPLETED][:15]
        for index, enrollment in enumerate(completed_enrollments, start=1):
            code = f"VIDYA-CERT-{index:04d}"
            certificates.append(
                Certificate(
                    student_id=enrollment.student_id,
                    workshop_id=enrollment.workshop_id,
                    issue_date=dt(-index),
                    verification_code=code,
                )
            )
        db.add_all(certificates)
        await db.flush()

        workshop_by_id = {workshop.id: workshop for workshop in workshops}
        student_by_id = {student.id: student for student in students}
        for certificate in certificates:
            student = student_by_id.get(certificate.student_id)
            workshop = workshop_by_id.get(certificate.workshop_id)
            if student and workshop:
                generate_certificate_pdf(
                    student_name=student.name or student.email,
                    workshop_title=workshop.title or "Workshop",
                    verification_code=certificate.verification_code or certificate.id,
                    certificate_id=certificate.id,
                )

        fee_plans: list[FeePlan] = []
        fee_plan_specs = [
            ("Monthly Standard", 2500, "monthly"),
            ("Monthly Plus", 3200, "monthly"),
            ("Quarterly Saver", 7200, "quarterly"),
            ("Quarterly Premium", 9000, "quarterly"),
            ("Semester Basic", 14000, "semester"),
            ("Semester Advanced", 18000, "semester"),
            ("Bootcamp Intensive", 22000, "one_time"),
            ("Professional Track", 26000, "one_time"),
            ("Certification Add-on", 3500, "one_time"),
            ("Weekend Track", 6000, "monthly"),
        ]
        for name, amount, billing_cycle in fee_plan_specs:
            fee_plans.append(FeePlan(name=name, amount=amount, billing_cycle=billing_cycle))
        db.add_all(fee_plans)
        await db.flush()

        student_fees: list[StudentFee] = []
        for index, student in enumerate(students[:15]):
            fee_plan = fee_plans[index % len(fee_plans)]
            student_fees.append(
                StudentFee(
                    student_id=student.id,
                    fee_plan_id=fee_plan.id,
                    balance=max(0, fee_plan.amount - (index % 4) * 1200),
                )
            )
        for index, student in enumerate(students[:5]):
            fee_plan = fee_plans[(index + 5) % len(fee_plans)]
            student_fees.append(
                StudentFee(
                    student_id=student.id,
                    fee_plan_id=fee_plan.id,
                    balance=max(0, fee_plan.amount - 800),
                )
            )
        db.add_all(student_fees)
        await db.flush()

        student_fees_by_student: dict[str, list[StudentFee]] = defaultdict(list)
        for fee in student_fees:
            student_fees_by_student[fee.student_id].append(fee)

        payments: list[Payment] = []
        for index, student in enumerate(students[:15]):
            payments.append(
                Payment(
                    student_id=student.id,
                    amount=1200 + (index % 4) * 500,
                    method=["upi", "card", "bank_transfer"][index % 3],
                    reference=f"PAY-{index + 1:04d}",
                    created_at=dt(-12 + index),
                )
            )
        for index, student in enumerate(students[:15]):
            payments.append(
                Payment(
                    student_id=student.id,
                    amount=800 + (index % 3) * 400,
                    method=["upi", "cash", "card"][index % 3],
                    reference=f"PAYX-{index + 1:04d}",
                    created_at=dt(-4 + index),
                )
            )
        db.add_all(payments)
        await db.flush()

        notifications: list[Notification] = []
        notification_users = [admin, *institution_admins[:4], *educators[:5], *students[:15]]
        notification_types = [
            NotificationType.GENERAL,
            NotificationType.TEST,
            NotificationType.FEES,
            NotificationType.ATTENDANCE,
            NotificationType.CERTIFICATE,
        ]
        for index, user in enumerate(notification_users):
            notifications.append(
                Notification(
                    user_id=user.id,
                    message=f"Demo notification {index + 1} for {user.name}.",
                    status=NotificationStatus.READ if index % 3 == 0 else NotificationStatus.UNREAD,
                    notification_type=notification_types[index % len(notification_types)],
                    created_at=dt(-index),
                )
            )
        db.add_all(notifications)
        await db.commit()

        print("[test_data] Loaded demo data into SQLite:")
        print(f"  institutions={len(institutions)}")
        print(f"  users={len(users)}")
        print(f"  workshops={len(workshops)}")
        print(f"  modules={len(modules)}")
        print(f"  enrollments={len(enrollments)}")
        print(f"  sessions={len(sessions)}")
        print(f"  attendance={len(attendance_rows)}")
        print(f"  assessments={len(assessments)}")
        print(f"  questions={len(questions)}")
        print(f"  submissions={len(submissions)}")
        print(f"  certificates={len(certificates)}")
        print(f"  fee_plans={len(fee_plans)}")
        print(f"  student_fees={len(student_fees)}")
        print(f"  payments={len(payments)}")
        print(f"  notifications={len(notifications)}")
        print("[test_data] Demo logins:")
        print("  admin@vidyasetu.edu / admin123")
        print("  institution.admin@vidyasetu.edu / institution123")
        print("  educator@vidyasetu.edu / educator123")
        print("  student@vidyasetu.edu / student123")


if __name__ == "__main__":
    asyncio.run(load_test_data())
