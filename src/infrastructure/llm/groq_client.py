"""Groq Cloud API adapter using OpenAI client compatibility."""

from __future__ import annotations

import logging

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI

from infrastructure.config import Settings
from infrastructure.llm.client import LLMClient, LLMRequest, LLMResponse
from infrastructure.llm.openai_client import LLMError

logger = logging.getLogger(__name__)


class GroqLLMClient:
    """LLM client for Groq using the OpenAI SDK compatibility layer."""

    def __init__(self, settings: Settings) -> None:
        if not settings.llm_api_key:
            raise ValueError("LLM_API_KEY is required for Groq provider")
        self._settings = settings
        self._client = OpenAI(
            api_key=settings.llm_api_key,
            base_url="https://api.groq.com/openai/v1",
            timeout=settings.llm_timeout_seconds,
        )

    def complete(self, request: LLMRequest) -> LLMResponse:
        model = request.model
        # Map OpenAI default model to Groq equivalent if configured
        if model == "gpt-4o-mini":
            model = "llama-3.3-70b-versatile"
            logger.info("Mapping OpenAI model 'gpt-4o-mini' to Groq model '%s'", model)

        kwargs: dict = {
            "model": model,
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
            raise LLMError(f"Groq connection/timeout: {exc}") from exc
        except APIStatusError as exc:
            if exc.status_code == 429:
                raise LLMError(f"Groq rate limit: {exc}") from exc
            raise LLMError(f"Groq API error: {exc}") from exc

        content = completion.choices[0].message.content or ""
        resp_model = completion.model or model
        logger.info("Groq completion received (%d chars)", len(content))
        return LLMResponse(content=content, model=resp_model, provider="groq")
