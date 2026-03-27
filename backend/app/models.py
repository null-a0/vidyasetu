import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func

# --------------------------------------------------
# BASE
# --------------------------------------------------


class Base(DeclarativeBase):
    pass


def generate_uuid():
    return str(uuid.uuid4())


# --------------------------------------------------
# ENUMS
# --------------------------------------------------

class UserRole(str, Enum):
    ADMIN = "admin"
    INSTITUTION_ADMIN = "institution_admin"
    EDUCATOR = "educator"
    STUDENT = "student"


class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"


class EnrollmentStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"


class QuestionType(str, Enum):
    MCQ = "mcq"
    MSQ = "msq"


class NotificationType(str, Enum):
    GENERAL = "general"
    TEST = "test"
    FEES = "fees"
    ATTENDANCE = "attendance"
    CERTIFICATE = "certificate"


# --------------------------------------------------
# INSTITUTION
# --------------------------------------------------

class Institution(Base):
    __tablename__ = "institutions"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    address = Column(Text)

    admin_id = Column(String, ForeignKey("users.id"))

    users = relationship("User", back_populates="institution", foreign_keys="User.institution_id")
    admin = relationship("User", foreign_keys=[admin_id])
    workshops = relationship("Workshop", back_populates="institution")


# --------------------------------------------------
# USERS
# --------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)

    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    role = Column(SqlEnum(UserRole))
    institution_id = Column(String, ForeignKey("institutions.id"))

    phone = Column(String)
    profile_photo = Column(String)
    theme = Column(String, default="light")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    institution = relationship("Institution", back_populates="users", foreign_keys=[institution_id])
    enrollments = relationship("Enrollment", back_populates="student")


# --------------------------------------------------
# WORKSHOP + MODULE
# --------------------------------------------------

class Workshop(Base):
    __tablename__ = "workshops"

    id = Column(String, primary_key=True, default=generate_uuid)

    title = Column(String)
    description = Column(Text)

    start_date = Column(DateTime)
    end_date = Column(DateTime)

    institution_id = Column(String, ForeignKey("institutions.id"))

    institution = relationship("Institution", back_populates="workshops")
    modules = relationship("Module", back_populates="workshop")
    assessments = relationship("Assessment", back_populates="workshop")


class Module(Base):
    __tablename__ = "modules"

    id = Column(String, primary_key=True, default=generate_uuid)

    workshop_id = Column(String, ForeignKey("workshops.id"))

    title = Column(String)
    order_index = Column(Integer)

    # Embedded materials
    materials = Column(JSON, default=list)
    """
    [
      {
        "id": "...",
        "title": "...",
        "type": "video/text/link",
        "content": "...",
        "created_at": "..."
      }
    ]
    """

    workshop = relationship("Workshop", back_populates="modules")
    assessments = relationship("Assessment", back_populates="module")


# --------------------------------------------------
# ENROLLMENT
# --------------------------------------------------

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(String, primary_key=True, default=generate_uuid)

    student_id = Column(String, ForeignKey("users.id"))
    workshop_id = Column(String, ForeignKey("workshops.id"))

    status = Column(SqlEnum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User", back_populates="enrollments")


# --------------------------------------------------
# SESSION + ATTENDANCE
# --------------------------------------------------

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=generate_uuid)

    workshop_id = Column(String, ForeignKey("workshops.id"))

    title = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(String, primary_key=True, default=generate_uuid)

    session_id = Column(String, ForeignKey("sessions.id"))
    student_id = Column(String, ForeignKey("users.id"))

    status = Column(String)


# --------------------------------------------------
# ASSESSMENTS
# --------------------------------------------------

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, default=generate_uuid)

    workshop_id = Column(String, ForeignKey("workshops.id"))
    module_id = Column(String, ForeignKey("modules.id"))

    title = Column(String)
    total_marks = Column(Integer, default=0)
    pass_mark = Column(Integer, default=0)  # minimum score to pass

    workshop = relationship("Workshop", back_populates="assessments")
    module = relationship("Module", back_populates="assessments")
    questions = relationship("Question", back_populates="assessment")


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=generate_uuid)

    assessment_id = Column(String, ForeignKey("assessments.id"))

    text = Column(Text)
    type = Column(SqlEnum(QuestionType))
    marks = Column(Integer)

    # Embedded options
    options = Column(JSON, default=list)
    """
    [
      {
        "id": "...",
        "text": "...",
        "is_correct": true
      }
    ]
    """

    assessment = relationship("Assessment", back_populates="questions")


# --------------------------------------------------
# SUBMISSION
# --------------------------------------------------

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=generate_uuid)

    student_id = Column(String, ForeignKey("users.id"))
    assessment_id = Column(String, ForeignKey("assessments.id"))

    score = Column(Integer)
    percentage = Column(Integer)
    pass_fail = Column(Boolean, nullable=True)  # True=pass, False=fail, None=ungraded

    # Embedded answers
    answers = Column(JSON, default=list)
    """
    [
      {
        "question_id": "...",
        "selected_option_id": "..."
      }
    ]
    """

    submitted_at = Column(DateTime(timezone=True), server_default=func.now())


# --------------------------------------------------
# CERTIFICATE
# --------------------------------------------------

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String, primary_key=True, default=generate_uuid)

    student_id = Column(String, ForeignKey("users.id"))
    workshop_id = Column(String, ForeignKey("workshops.id"))

    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    verification_code = Column(String, unique=True)


# --------------------------------------------------
# FEES + PAYMENTS
# --------------------------------------------------

class FeePlan(Base):
    __tablename__ = "fee_plans"

    id = Column(String, primary_key=True, default=generate_uuid)

    name = Column(String)
    amount = Column(Integer)
    billing_cycle = Column(String)


class StudentFee(Base):
    __tablename__ = "student_fees"

    id = Column(String, primary_key=True, default=generate_uuid)

    student_id = Column(String, ForeignKey("users.id"))
    fee_plan_id = Column(String, ForeignKey("fee_plans.id"))

    balance = Column(Integer)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=generate_uuid)

    student_id = Column(String, ForeignKey("users.id"))

    amount = Column(Integer)
    method = Column(String)
    reference = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# --------------------------------------------------
# NOTIFICATIONS
# --------------------------------------------------

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=generate_uuid)

    user_id = Column(String, ForeignKey("users.id"))

    message = Column(Text, nullable=False)
    status = Column(SqlEnum(NotificationStatus),
                    default=NotificationStatus.UNREAD)
    notification_type = Column(
        SqlEnum(NotificationType), default=NotificationType.GENERAL
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --------------------------------------------------
# APPROVAL REQUESTS (minimal workflow for admin panels)
# --------------------------------------------------

class ApprovalRequestType(str, Enum):
    DELETE_STUDENT = "delete_student"
    DELETE_EDUCATOR = "delete_educator"
    DELETE_WORKSHOP = "delete_workshop"


class ApprovalRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(String, primary_key=True, default=generate_uuid)

    request_type = Column(SqlEnum(ApprovalRequestType), nullable=False)
    status = Column(SqlEnum(ApprovalRequestStatus), default=ApprovalRequestStatus.PENDING)

    # Generic payload so we can add request types without schema churn.
    payload = Column(JSON, default=dict)

    requested_by = Column(String, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


# --------------------------------------------------
# EDUCATOR SALARY PAYMENTS (minimal bookkeeping for admin salary page)
# --------------------------------------------------

class SalaryPaymentStatus(str, Enum):
    PAID = "paid"
    UNPAID = "unpaid"


class SalaryPayment(Base):
    __tablename__ = "salary_payments"

    id = Column(String, primary_key=True, default=generate_uuid)

    educator_id = Column(String, ForeignKey("users.id"), nullable=False)
    month = Column(String, nullable=False)  # YYYY-MM
    amount = Column(Integer, default=0)
    status = Column(SqlEnum(SalaryPaymentStatus), default=SalaryPaymentStatus.PAID)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
