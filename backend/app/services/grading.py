"""
app/services/grading.py
-----------------------
Pure, synchronous auto-grading logic for MCQ and MSQ questions.
The grading service is kept DB-free so it can be unit-tested with no setup.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QuestionResult:
    question_id: str
    earned: int
    max_marks: int
    correct: bool


@dataclass
class GradingReport:
    score: int
    total_marks: int
    pass_fail: bool
    details: list[QuestionResult] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        if self.total_marks == 0:
            return 0.0
        return round((self.score / self.total_marks) * 100, 2)


def _correct_ids(options: list[dict]) -> set[str]:
    """Return the set of option IDs marked as correct."""
    return {opt["id"] for opt in options if opt.get("is_correct")}


def grade_submission(
    questions: list[Any],
    answers: list[dict],
    pass_mark: int = 0,
) -> GradingReport:
    """Auto-grade MCQ / MSQ submission.

    Args:
        questions: List of SQLAlchemy Question ORM objects (or anything with
                   ``.id``, ``.type``, ``.marks``, ``.options`` attributes).
        answers:   List of raw answer dicts from ``Submission.answers`` JSON column.
                   Each dict must have ``question_id`` and ``selected_option_ids``.
        pass_mark: Minimum score required to pass (0 = no pass threshold).

    Returns:
        :class:`GradingReport` with per-question breakdown.
    """
    # Build answer lookup: question_id → set of selected option ids
    answer_map: dict[str, set[str]] = {}
    for ans in answers:
        qid = ans.get("question_id", "")
        ids = ans.get("selected_option_ids", [])
        # Backwards compat: single string field
        if not ids and ans.get("selected_option_id"):
            ids = [ans["selected_option_id"]]
        answer_map[qid] = set(ids)

    total_marks = 0
    score = 0
    details: list[QuestionResult] = []

    for q in questions:
        q_max = q.marks or 0
        total_marks += q_max
        q_type = (str(q.type.value) if hasattr(q.type, "value") else str(q.type)).lower()
        options: list[dict] = q.options or []
        correct_ids = _correct_ids(options)
        selected_ids = answer_map.get(q.id, set())

        if q_type == "mcq":
            # MCQ: exactly one correct; award full marks if selected matches
            if len(selected_ids) == 1 and selected_ids == correct_ids:
                earned = q_max
            else:
                earned = 0
        elif q_type == "msq":
            # MSQ: partial credit per correct option selected, penalise wrong picks
            # Strategy: +1 per correct selected, -1 per wrong selected, floor 0
            n_correct = len(correct_ids)
            if n_correct == 0:
                earned = 0
            else:
                hits = len(selected_ids & correct_ids)
                misses = len(selected_ids - correct_ids)
                raw = hits - misses
                # Scale to question marks
                earned = max(0, round((raw / n_correct) * q_max))
        else:
            # Unknown / open-ended: skip auto-grade
            earned = 0

        score += earned
        details.append(
            QuestionResult(
                question_id=q.id,
                earned=earned,
                max_marks=q_max,
                correct=(earned == q_max),
            )
        )

    pass_fail = score >= pass_mark
    return GradingReport(score=score, total_marks=total_marks, pass_fail=pass_fail, details=details)
