"""OpenAI chat completions adapter."""

from __future__ import annotations

import logging

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI

from infrastructure.config import Settings
from infrastructure.llm.client import LLMClient, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when the LLM provider fails (EC-LLM-01, EC-LLM-02)."""


class OpenAILLMClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.llm_api_key:
            raise ValueError("LLM_API_KEY is required for OpenAI provider")
        self._settings = settings
        self._client = OpenAI(
            api_key=settings.llm_api_key,
            timeout=settings.llm_timeout_seconds,
        )

    def complete(self, request: LLMRequest) -> LLMResponse:
        kwargs: dict = {
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
        }
        if request.json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            completion = self._client.chat.completions.create(**kwargs)
        except (APITimeoutError, APIConnectionError) as exc:
            raise LLMError(f"OpenAI connection/timeout: {exc}") from exc
        except APIStatusError as exc:
            if exc.status_code == 429:
                raise LLMError(f"OpenAI rate limit: {exc}") from exc
            raise LLMError(f"OpenAI API error: {exc}") from exc

        content = completion.choices[0].message.content or ""
        model = completion.model or request.model
        logger.info("OpenAI completion received (%d chars)", len(content))
        return LLMResponse(content=content, model=model, provider="openai")
