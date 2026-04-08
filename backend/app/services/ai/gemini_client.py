from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import settings
from app.services.ai.retry import RetryPolicy, run_with_retry


class GeminiError(Exception):
    pass


class GeminiTransientError(GeminiError):
    pass


class GeminiResponseFormatError(GeminiError):
    pass


@dataclass(frozen=True)
class GeminiUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True)
class GeminiGenerationResult:
    raw_output: str
    parsed_output: dict[str, Any]
    usage: GeminiUsage
    retries_used: int = 0


class GeminiClient:
    """Backend-only Gemini wrapper with schema-constrained JSON output."""

    _TRANSIENT_CODES = {408, 409, 429, 500, 502, 503, 504}

    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        api_base_url: str,
        timeout_seconds: float = 30.0,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiClient.")

        self.api_key = api_key
        normalized_model_name = model_name.strip().removeprefix("models/").strip()
        if not normalized_model_name:
            raise ValueError("GEMINI_MODEL_NAME must be set.")
        self.model_name = normalized_model_name
        self.api_base_url = api_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.retry_policy = retry_policy or RetryPolicy()

    @classmethod
    def from_settings(cls) -> "GeminiClient":
        return cls(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_MODEL_NAME,
            api_base_url=settings.GEMINI_API_BASE_URL,
            timeout_seconds=settings.GEMINI_TIMEOUT_SECONDS,
            retry_policy=RetryPolicy(
                max_attempts=max(settings.AI_MAX_RETRIES, 1),
                base_delay_seconds=max(settings.AI_RETRY_BASE_DELAY_SECONDS, 0.1),
            ),
        )

    async def generate_structured(
        self,
        *,
        prompt: str,
        response_json_schema: dict[str, Any],
        temperature: float = 0.2,
    ) -> GeminiGenerationResult:
        async def _task() -> GeminiGenerationResult:
            return await self._generate_once(
                prompt=prompt,
                response_json_schema=response_json_schema,
                temperature=temperature,
            )

        result, retries_used = await run_with_retry(
            _task,
            should_retry=self._should_retry,
            policy=self.retry_policy,
        )
        return GeminiGenerationResult(
            raw_output=result.raw_output,
            parsed_output=result.parsed_output,
            usage=result.usage,
            retries_used=retries_used,
        )

    async def _generate_once(
        self,
        *,
        prompt: str,
        response_json_schema: dict[str, Any],
        temperature: float,
    ) -> GeminiGenerationResult:
        url = f"{self.api_base_url}/v1beta/models/{self.model_name}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
                "responseSchema": response_json_schema,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(url, params={"key": self.api_key}, json=payload)
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            raise GeminiTransientError(f"Transport error while calling Gemini: {exc}") from exc

        if response.status_code in self._TRANSIENT_CODES:
            raise GeminiTransientError(
                f"Transient Gemini error {response.status_code}: {response.text[:300]}"
            )
        if response.status_code == 404:
            raise GeminiError(
                "Gemini model not found for generateContent. "
                f"Configured GEMINI_MODEL_NAME='{self.model_name}'. "
                "Set a currently available stable model (for example: gemini-3.1-flash-lite-preview) "
                "and verify with the ListModels endpoint. "
                f"Raw: {response.text[:500]}"
            )
        if response.status_code >= 400:
            raise GeminiError(f"Gemini error {response.status_code}: {response.text[:600]}")

        data = response.json()
        raw_output = self._extract_response_text(data)
        if not raw_output:
            raise GeminiResponseFormatError("Gemini response did not contain JSON text content.")

        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise GeminiResponseFormatError("Gemini response was not valid JSON.") from exc

        if not isinstance(parsed, dict):
            raise GeminiResponseFormatError("Gemini structured response must be a JSON object.")

        usage_meta = data.get("usageMetadata", {}) or {}
        usage = GeminiUsage(
            input_tokens=usage_meta.get("promptTokenCount"),
            output_tokens=usage_meta.get("candidatesTokenCount"),
            total_tokens=usage_meta.get("totalTokenCount"),
        )
        return GeminiGenerationResult(raw_output=raw_output, parsed_output=parsed, usage=usage)

    @staticmethod
    def _extract_response_text(response_json: dict[str, Any]) -> str:
        candidates = response_json.get("candidates") or []
        if not candidates:
            return ""
        parts = (((candidates[0] or {}).get("content") or {}).get("parts")) or []
        if not parts:
            return ""
        return str((parts[0] or {}).get("text") or "").strip()

    @staticmethod
    def _should_retry(exc: Exception) -> bool:
        return isinstance(exc, GeminiTransientError)
