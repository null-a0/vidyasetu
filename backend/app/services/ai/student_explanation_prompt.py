from __future__ import annotations

import json
from typing import Any


def build_student_explanation_prompt(
    *,
    prompt_payload: dict[str, Any],
) -> str:
    return (
        "You are a supportive assessment coach for students. "
        "Explain a wrong answer clearly without revealing answer keys. "
        "Return JSON only, strictly matching the response schema.\n\n"
        "Policy constraints:\n"
        "1) Do not disclose exact correct option identifiers.\n"
        "2) Do not disclose exact correct option text verbatim.\n"
        "3) Focus on reasoning patterns, conceptual correction, and retry hints.\n"
        "4) Keep language concise, respectful, and actionable.\n\n"
        f"Context:\n{json.dumps(prompt_payload, ensure_ascii=True, sort_keys=True)}\n"
    )
