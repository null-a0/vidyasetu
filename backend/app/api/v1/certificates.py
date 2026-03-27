from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_current_user, get_db, require_role
from app.config import settings
from app.crud.crud_misc import (
    create_certificate,
    get_certificate,
    get_certificate_by_code,
    get_certificates_by_student,
)
from app.crud.crud_user import get_user
from app.crud.crud_workshop import get_workshop
from app.models import Certificate, User, UserRole, Workshop
from app.schemas.base import Page
from app.schemas.misc import CertificateCreate, CertificateResponse
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
    r = CertificateResponse.model_validate(cert)
    r.qr_url = _build_qr_url(r.verification_code or "")
    r.pdf_path = f"media/certificates/{r.id}.pdf"

    if r.student_id:
        student = await get_user(db, r.student_id)
        if student:
            r.student_name = student.name

    if r.workshop_id:
        workshop = await get_workshop(db, r.workshop_id)
        if workshop:
            r.workshop_title = workshop.title

    return r


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
    q = select(Certificate).order_by(Certificate.issue_date.desc())

    # Institution-scoped list for non-admin staff.
    if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        q = (
            q.join(Workshop, Workshop.id == Certificate.workshop_id)
            .where(Workshop.institution_id == current_user.institution_id)
        )

    total = (
        await db.execute(select(func.count()).select_from(q.subquery()))
    ).scalar_one()
    items = (await db.execute(q.offset(page.offset).limit(page.limit))).scalars().all()

    enriched = [await _enrich(db, c) for c in items]
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

    code = generate_verification_code()
    cert = await create_certificate(db, payload, verification_code=code)

    background_tasks.add_task(
        _pdf_background,
        student_name=student.name or "Student",
        workshop_title=workshop.title or "Workshop",
        verification_code=code,
        cert_id=cert.id,
    )

    response = CertificateResponse.model_validate(cert)
    response.qr_url = _build_qr_url(code)
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

    # Students can only see their own certificate.
    if current_user.role == UserRole.STUDENT and cert.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    # Non-admin staff are restricted to their institution.
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

    items, total = await get_certificates_by_student(
        db, student_id, offset=page.offset, limit=page.limit
    )

    enriched = [await _enrich(db, c) for c in items]
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No certificate found with this verification code.",
        )

    response = await _enrich(db, cert)
    response.qr_url = _build_qr_url(verification_code)
    return response
