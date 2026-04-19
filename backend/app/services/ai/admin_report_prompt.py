from __future__ import annotations

import json
from typing import Any


def build_admin_report_prompt(
    *,
    request_payload: dict[str, Any],
    analytics_context: dict[str, Any],
) -> str:
    return (
        "You are an analytics assistant for an education platform. "
        "Generate an actionable report for admin stakeholders. "
        "Return JSON only, strictly following the provided schema.\n\n"
        "Guidelines:\n"
        "1) Keep summary concise and concrete.\n"
        "2) Prioritize measurable insights and risk flags.\n"
        "3) Recommendations must be operational and prioritized.\n"
        "4) Mention caveats where data may be incomplete.\n\n"
        f"Request Payload:\n{json.dumps(request_payload, ensure_ascii=True, sort_keys=True)}\n\n"
        f"Analytics Context:\n{json.dumps(analytics_context, ensure_ascii=True, sort_keys=True)}\n"
    )
