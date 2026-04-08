from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models import AIFeatureType, AIGenerationStatus


class AITokenUsage(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


class AIGenerationCreate(BaseModel):
    feature_type: AIFeatureType
    requester_user_id: str
    institution_id: str | None = None
    source_entity_type: str
    source_entity_id: str
    prompt_version: str
    model_name: str
    raw_prompt_input: dict[str, Any]
    request_fingerprint: str
    cache_expires_at: datetime | None = None


class AIGenerationUpdate(BaseModel):
    status: AIGenerationStatus | None = None
    raw_model_output: str | None = None
    parsed_output_json: dict[str, Any] | None = None
    error_details: dict[str, Any] | None = None
    retry_count: int | None = None
    token_usage: AITokenUsage | None = None
    cache_expires_at: datetime | None = None


class AdminReportDataWindow(BaseModel):
    start_date: str | None = None
    end_date: str | None = None
    scope: str


class AdminReportRecommendationItem(BaseModel):
    title: str
    action: str
    rationale: str
    priority: str = Field(description="low|medium|high")


class AdminReportStructuredOutput(BaseModel):
    summary: str
    key_insights: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    recommendations: list[AdminReportRecommendationItem] = Field(default_factory=list)
    trend_highlights: list[str] = Field(default_factory=list)
    data_window: AdminReportDataWindow
    caveats: list[str] = Field(default_factory=list)


ADMIN_REPORT_RESPONSE_JSON_SCHEMA = AdminReportStructuredOutput.model_json_schema()


class StudentExplanationStructuredOutput(BaseModel):
    why_it_was_wrong: str
    correct_reasoning: str
    common_mistake: str
    hint_for_retry: str
    confidence: float = Field(ge=0.0, le=1.0)
    follow_up_questions: list[str] = Field(default_factory=list)


STUDENT_EXPLANATION_RESPONSE_JSON_SCHEMA = StudentExplanationStructuredOutput.model_json_schema()


class AdminAIReportCreateRequest(BaseModel):
    institution_id: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    focus_areas: list[str] = Field(default_factory=list)
    force_regenerate: bool = False


class AdminAIReportCreateResponse(BaseModel):
    report_id: str
    status: AIGenerationStatus
    from_cache: bool
    deduplicated: bool


class AdminAIReportStatusResponse(BaseModel):
    report_id: str
    status: AIGenerationStatus
    error_details: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AdminAIReportResultResponse(BaseModel):
    report_id: str
    status: AIGenerationStatus
    result: AdminReportStructuredOutput
    created_at: datetime | None = None
    updated_at: datetime | None = None
    prompt_version: str
    model_name: str


class AdminAIReportListItem(BaseModel):
    report_id: str
    status: AIGenerationStatus
    institution_id: str | None = None
    source_entity_type: str
    source_entity_id: str
    prompt_version: str
    model_name: str
    summary_preview: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class StudentExplanationCreateRequest(BaseModel):
    submission_id: str
    question_id: str
    force_regenerate: bool = False


class StudentExplanationCreateResponse(BaseModel):
    explanation_id: str
    status: AIGenerationStatus
    from_cache: bool
    explanation: StudentExplanationStructuredOutput
