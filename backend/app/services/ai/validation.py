from __future__ import annotations

from pydantic import ValidationError

from app.schemas.ai import AdminReportStructuredOutput


class StructuredOutputValidationError(ValueError):
    pass


def validate_admin_report_output(payload: object) -> AdminReportStructuredOutput:
    try:
        return AdminReportStructuredOutput.model_validate(payload)
    except ValidationError as exc:
        raise StructuredOutputValidationError(str(exc)) from exc
