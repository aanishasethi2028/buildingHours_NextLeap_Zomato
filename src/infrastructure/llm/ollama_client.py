"""Ollama local API adapter."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request

from infrastructure.config import Settings
from infrastructure.llm.client import LLMRequest, LLMResponse
from infrastructure.llm.openai_client import LLMError

logger = logging.getLogger(__name__)


class OllamaLLMClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._base_url = settings.ollama_base_url.rstrip("/")

    def complete(self, request: LLMRequest) -> LLMResponse:
        payload = {
            "model": request.model,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "stream": False,
            "options": {"temperature": request.temperature},
        }
        if request.json_mode:
            payload["format"] = "json"

        url = f"{self._base_url}/api/chat"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._settings.llm_timeout_seconds) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise LLMError(f"Ollama unavailable at {url}: {exc}") from exc

        content = body.get("message", {}).get("content", "")
        logger.info("Ollama completion received (%d chars)", len(content))
        return LLMResponse(content=content, model=request.model, provider="ollama")
