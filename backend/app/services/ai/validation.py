from __future__ import annotations

from pydantic import ValidationError

from app.schemas.ai import AdminReportStructuredOutput, StudentExplanationStructuredOutput


class StructuredOutputValidationError(ValueError):
    pass


def validate_admin_report_output(payload: object) -> AdminReportStructuredOutput:
    try:
        return AdminReportStructuredOutput.model_validate(payload)
    except ValidationError as exc:
        raise StructuredOutputValidationError(str(exc)) from exc


def _normalize_text(value: str) -> str:
    return " ".join(value.lower().strip().split())


def validate_student_explanation_output(
    payload: object,
    *,
    disallowed_option_ids: list[str] | None = None,
    disallowed_option_texts: list[str] | None = None,
) -> StudentExplanationStructuredOutput:
    try:
        validated = StudentExplanationStructuredOutput.model_validate(payload)
    except ValidationError as exc:
        raise StructuredOutputValidationError(str(exc)) from exc

    disallowed_ids = {
        _normalize_text(value)
        for value in (disallowed_option_ids or [])
        if isinstance(value, str) and value.strip()
    }
    disallowed_texts = {
        _normalize_text(value)
        for value in (disallowed_option_texts or [])
        if isinstance(value, str) and len(value.strip()) >= 5
    }
    combined_text = " ".join(
        [
            validated.why_it_was_wrong,
            validated.correct_reasoning,
            validated.common_mistake,
            validated.hint_for_retry,
            *validated.follow_up_questions,
        ]
    )
    normalized_output = _normalize_text(combined_text)

    for option_id in disallowed_ids:
        if option_id in normalized_output:
            raise StructuredOutputValidationError(
                "Policy violation: explanation leaked an answer option identifier."
            )

    for option_text in disallowed_texts:
        if option_text in normalized_output:
            raise StructuredOutputValidationError(
                "Policy violation: explanation leaked exact answer-key text."
            )

    return validated
