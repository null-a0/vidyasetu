from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_current_user, get_db, require_role
from app.config import settings
from app.crud.crud_misc import (
    create_certificate,
    create_notification,
    get_certificate,
    get_certificate_by_code,
    get_certificates_by_student,
)
from app.crud.crud_user import get_user
from app.crud.crud_workshop import get_workshop
from app.models import Certificate, NotificationType, User, UserRole, Workshop
from app.schemas.base import Page
from app.schemas.misc import (
    CertificateCreate,
    CertificateDownloadResponse,
    CertificateRecommendationRequest,
    CertificateRecommendationResponse,
    CertificateResponse,
    NotificationCreate,
)
from app.services.certificate import generate_certificate_pdf, generate_verification_code

router = APIRouter(prefix="/certificates", tags=["certificates"])

_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)

_BASE_URL = getattr(settings, "BASE_URL", "http://localhost:8000")


def _build_qr_url(verification_code: str) -> str:
    return f"{_BASE_URL}/api/v1/certificates/verify/{verification_code}"


def _pdf_background(
    student_name: str,
    workshop_title: str,
    verification_code: str,
    cert_id: str,
) -> None:
    generate_certificate_pdf(
        student_name=student_name,
        workshop_title=workshop_title,
        verification_code=verification_code,
        certificate_id=cert_id,
    )


async def _enrich(db: AsyncSession, cert: Certificate) -> CertificateResponse:
    response = CertificateResponse.model_validate(cert)
    response.qr_url = _build_qr_url(response.verification_code or "")
    response.pdf_path = f"media/certificates/{response.id}.pdf"

    if response.student_id:
        student = await get_user(db, response.student_id)
        if student:
            response.student_name = student.name

    if response.workshop_id:
        workshop = await get_workshop(db, response.workshop_id)
        if workshop:
            response.workshop_title = workshop.title

    return response


@router.get(
    "/",
    response_model=Page[CertificateResponse],
    summary="List all certificates (staff only)",
)
async def list_all(
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(*_STAFF)),
) -> Page[CertificateResponse]:
    query = select(Certificate).order_by(Certificate.issue_date.desc())

    if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        query = (
            query.join(Workshop, Workshop.id == Certificate.workshop_id)
            .where(Workshop.institution_id == current_user.institution_id)
        )

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    items = (await db.execute(query.offset(page.offset).limit(page.limit))).scalars().all()

    enriched = [await _enrich(db, certificate) for certificate in items]
    return Page(items=enriched, total=int(total or 0), offset=page.offset, limit=page.limit)


@router.post(
    "/generate",
    response_model=CertificateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a certificate for a student (staff only)",
)
async def generate_certificate(
    payload: CertificateCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(*_STAFF)),
) -> CertificateResponse:
    student = await get_user(db, payload.student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    workshop = await get_workshop(db, payload.workshop_id)
    if not workshop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workshop not found.")

    if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        if workshop.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    verification_code = generate_verification_code()
    cert = await create_certificate(db, payload, verification_code=verification_code)

    background_tasks.add_task(
        _pdf_background,
        student_name=student.name or "Student",
        workshop_title=workshop.title or "Workshop",
        verification_code=verification_code,
        cert_id=cert.id,
    )

    response = CertificateResponse.model_validate(cert)
    response.qr_url = _build_qr_url(verification_code)
    response.pdf_path = f"media/certificates/{cert.id}.pdf"
    response.student_name = student.name
    response.workshop_title = workshop.title
    return response


@router.get(
    "/{certificate_id}",
    response_model=CertificateResponse,
    summary="Fetch a certificate by ID",
)
async def get_one(
    certificate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CertificateResponse:
    cert = await get_certificate(db, certificate_id)
    if not cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found.")

    if current_user.role == UserRole.STUDENT and cert.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        workshop = await get_workshop(db, cert.workshop_id)
        if not workshop or workshop.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    return await _enrich(db, cert)


@router.get(
    "/student/{student_id}",
    response_model=Page[CertificateResponse],
    summary="List all certificates for a student",
)
async def list_by_student(
    student_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[CertificateResponse]:
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    items, total = await get_certificates_by_student(db, student_id, offset=page.offset, limit=page.limit)
    enriched = [await _enrich(db, certificate) for certificate in items]
    return Page(items=enriched, total=int(total or 0), offset=page.offset, limit=page.limit)


@router.get(
    "/verify/{verification_code}",
    response_model=CertificateResponse,
    summary="Publicly verify a certificate by its verification code (no auth required)",
)
async def verify_certificate(
    verification_code: str,
    db: AsyncSession = Depends(get_db),
) -> CertificateResponse:
    cert = await get_certificate_by_code(db, verification_code)
    if not cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No certificate found with this verification code.")

    response = await _enrich(db, cert)
    response.qr_url = _build_qr_url(verification_code)
    return response


@router.post(
    "/recommend",
    response_model=CertificateRecommendationResponse,
    summary="Recommend a student for certification and persist communication trail",
)
async def recommend_certificate(
    payload: CertificateRecommendationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EDUCATOR, UserRole.INSTITUTION_ADMIN, UserRole.ADMIN)),
) -> CertificateRecommendationResponse:
    student = await get_user(db, payload.student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    workshop = await get_workshop(db, payload.workshop_id)
    if not workshop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workshop not found.")

    if current_user.role in (UserRole.EDUCATOR, UserRole.INSTITUTION_ADMIN):
        if workshop.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    institution_admin_ids = (
        await db.execute(
            select(User.id)
            .where(User.role == UserRole.INSTITUTION_ADMIN)
            .where(User.institution_id == workshop.institution_id)
        )
    ).scalars().all()

    recipients = set(institution_admin_ids)
    if not recipients and current_user.role == UserRole.ADMIN and student.id:
        recipients.add(student.id)

    accepted = 0
    failed = 0
    note = (payload.note or "").strip()
    message = (
        f"[Certificate Recommendation] {student.name or student.email} for "
        f"{workshop.title or 'workshop'} by {current_user.name or current_user.email}."
    )
    if note:
        message = f"{message} Note: {note}"

    for recipient_id in recipients:
        try:
            await create_notification(
                db,
                NotificationCreate(
                    user_id=recipient_id,
                    message=message,
                    notification_type=NotificationType.CERTIFICATE,
                ),
            )
            accepted += 1
        except Exception:
            failed += 1

    return CertificateRecommendationResponse(
        accepted=accepted,
        failed=failed,
        message="Certificate recommendation recorded.",
    )


@router.get(
    "/{certificate_id}/download",
    response_model=CertificateDownloadResponse,
    summary="Get protected certificate download URL",
)
async def certificate_download_url(
    certificate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CertificateDownloadResponse:
    cert = await get_certificate(db, certificate_id)
    if not cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found.")

    if current_user.role == UserRole.STUDENT and cert.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        workshop = await get_workshop(db, cert.workshop_id)
        if not workshop or workshop.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    relative_pdf = f"media/certificates/{cert.id}.pdf"
    if not Path(relative_pdf).exists():
        student = await get_user(db, cert.student_id) if cert.student_id else None
        workshop = await get_workshop(db, cert.workshop_id) if cert.workshop_id else None
        generate_certificate_pdf(
            student_name=(student.name if student else "Student"),
            workshop_title=(workshop.title if workshop else "Workshop"),
            verification_code=cert.verification_code or generate_verification_code(),
            certificate_id=cert.id,
        )

    return CertificateDownloadResponse(
        certificate_id=cert.id,
        download_url=f"{_BASE_URL}/{relative_pdf}",
    )
