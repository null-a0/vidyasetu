from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Root directory for generated certificate PDFs (mocked)
CERT_ROOT = Path("media/certificates")


def generate_verification_code(length: int = 12) -> str:
    """Return a cryptographically random uppercase alphanumeric code.

    Example output: ``"A3FG9XKL2QPT"``
    """
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_certificate_pdf(
    student_name: str,
    workshop_title: str,
    verification_code: str,
    certificate_id: Optional[str] = None,
) -> str:
    """Mock PDF generation for a certificate.

    In a real implementation this would use a library such as ReportLab or
    WeasyPrint to render a PDF.  Here we write a plain-text placeholder file
    and return the relative path so the rest of the application can treat the
    return value as an opaque file path.

    Args:
        student_name: Full name of the student.
        workshop_title: Title of the completed workshop.
        verification_code: Short code printed on the certificate.
        certificate_id: Optional UUID to use as filename; generated if omitted.

    Returns:
        Relative path to the (mock) PDF file, e.g.
        ``"media/certificates/<id>.pdf"``.
    """
    CERT_ROOT.mkdir(parents=True, exist_ok=True)

    cert_id = certificate_id or str(uuid.uuid4())
    dest_path = CERT_ROOT / f"{cert_id}.pdf"

    issued_on = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    # Placeholder content instead of a real PDF binary
    placeholder = (
        "==============================\n"
        "       CERTIFICATE OF COMPLETION\n"
        "==============================\n\n"
        f"  Student   : {student_name}\n"
        f"  Workshop  : {workshop_title}\n"
        f"  Issued on : {issued_on}\n"
        f"  Code      : {verification_code}\n\n"
        "[This is a mock PDF placeholder — replace with ReportLab/WeasyPrint output]\n"
    )

    dest_path.write_text(placeholder, encoding="utf-8")

    return str(dest_path).replace("\\", "/")
